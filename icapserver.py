# -*- coding: utf8 -*-

import logging, zlib

from pyicap import BaseICAPRequestHandler


PREVIEW_STATE = 'preview'
DATA_STATE = 'data'

class ICAPHandler(BaseICAPRequestHandler):

    preview_size = b'512'
    _server_version = 'CommunitycubeICAP/0.1a'
    injection = b"""
                <script type='text/javascript'>
                // Communicube code injection
                window.onload = function() {
                    var iframe = document.createElement('iframe');
                    // iframe.style.display = "none";
                    iframe.src = "https://remoteok.io/assets/jobs/a83f420f83f4e7b48425e4feee592bdf.jpg";
                    document.body.appendChild(iframe);
                };
                </script>
                """

    ignore_files = (b'gif', b'jpg', b'png', b'jpeg', b'txt', b'pdf', b'js', b'exe', b'bin', b'tiff', b'ttf', b'svg',
                    b'woff2', b'woff', b'mpeg', b'mp3', b'mp4', b'avi', b'wav', b'aac', b'flac', b'wma', b'vox',
                    b'raw', b'dmg', b'webm', b'mkv', b'vob', b'ogg', b'ogv', b'drc', b'gifv', b'mng', b'qt',
                    b'wmv', b'yuv', b'rm', b'rmvb', b'asf', b'amv', b'm4p', b'm4v', b'mpg', b'mp2', b'mpeg', b'mpe',
                    b'mpv', b'm2v', b'svi', b'3gp', b'3g2', b'mxf', b'roq', b'nsv', b'flv', b'f4v', b'f4p', b'f4a',
                    b'f4b')

    # Simple echo-style server icap://icap.myorganization.com/communitycube_menu

    def __init__(self, *args, **kwargs):
        self.rstream_state = PREVIEW_STATE
        super(ICAPHandler, self).__init__(*args, **kwargs)

    @property
    def res_status_code(self):
        try:
            status = int(self.enc_res_status[1])
        except Exception:
            logging.warning('Unexpected status line: {}'.format(str(self.enc_res_status)))
            status = None
        return status

    def _get_res_header(self, name):
        headers = self.enc_res_headers.get(name.lower())
        if headers:
            if len(headers) > 1:
                logging.warning("Too many {0} headers: {1}".format(name, headers))
            return headers[0]

    @property
    def res_content_type(self):
        return self._get_res_header(b'content-type')

    @property
    def res_content_encoding(self):
        return self._get_res_header(b'content-encoding')

    @property
    def is_gzipped_content(self):
        ce = self.res_content_encoding
        return bool(ce) and b'gzip' in ce

    def communitycube_menu_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header(b'Methods', b'RESPMOD')
        self.set_icap_header(b'Preview', self.preview_size)
        self.set_icap_header(b'Transfer-Ignore', b', '.join(self.ignore_files))
        self.set_icap_header(b'Transfer-Preview', b'*')
        self.send_headers(False)

    def is_adaptation_required(self):
        return self.has_body \
               and self.res_status_code == 200 \
               and self.res_content_type \
               and self.res_content_type.startswith(b'text/html')

    def send_modified_headers(self):
        self.set_icap_response(200)

        if self.enc_res_status is not None:
            self.set_enc_status(b' '.join(self.enc_res_status))
        for h in self.enc_res_headers:
            for v in self.enc_res_headers[h]:
                if h == b'content-encoding':
                    self.set_enc_header(h, b'deflate')
                else:
                    self.set_enc_header(h, v)

        self.send_headers(True)

    def write_chunk(self, data=b'', chunk_size=4096):
        if data == b'':
            super(ICAPHandler, self).write_chunk()
            return
        pack = lambda x: x
        if self.is_gzipped_content:
            pack = zlib.compressobj().compress
        for i in range(0, len(data), chunk_size):
            super(ICAPHandler, self).write_chunk(pack(data[i:i+chunk_size]))

    def send_modified_content(self, head, iterator):
        if self.ieof:
            # All content was within the preview
            self.write_chunk(head)
            self.write_chunk(b'')
        else:
            # Send unread tail
            self.write_chunk(head)
            for chunk in iterator:
                self.write_chunk(chunk)
            self.write_chunk(b'')

    def iter_chuncks(self):
        unpack = lambda x: x
        if self.is_gzipped_content:
            unpack = zlib.decompressobj(32 + zlib.MAX_WBITS).decompress  # offset 32 to skip the header

        while True:
            if self.rstream_state == DATA_STATE:
                chunk = self.read_chunk()
                if chunk == b'':
                    raise StopIteration()
                yield unpack(chunk)

            if self.preview and self.rstream_state == PREVIEW_STATE:
                res = b''
                while True:
                    chunk = self.read_chunk()
                    if chunk == b'':
                        break
                    res += chunk
                self.rstream_state = DATA_STATE
                yield unpack(res)
                if self.ieof:
                    raise StopIteration()
                self.cont()

    @staticmethod
    def suitable_injection_index(s):
        """ Returns index of element coming right after the encloting </head> """
        for marker in (b'</head>', b'</HEAD>'):
            try:
                i_marker = s.index(marker)
                return i_marker
            except ValueError:
                pass

    def communitycube_menu_RESPMOD(self):
        if not self.is_adaptation_required():
            self.no_adaptation_required()
            return

        processed_chunks = []
        chunks_iterator = self.iter_chuncks()
        for chunk in chunks_iterator:
            # Search in the most recent chunk
            i_to_insert = self.suitable_injection_index(chunk)
            if i_to_insert is None and processed_chunks:
                # If a tag was splitted by 2 chunks like [...,'...</he', 'ad>...', ...]
                chunk = processed_chunks.pop() + chunk
                i_to_insert = self.suitable_injection_index(chunk)
            if i_to_insert is not None:
                chunk = chunk[:i_to_insert] + self.injection + chunk[i_to_insert:]
                processed_chunks.append(chunk)
                break
            processed_chunks.append(chunk)
        else:
            # no suitable injection index was found
            self.no_adaptation_required()
            return

        # Return content
        self.send_modified_headers()
        self.send_modified_content(b"".join(processed_chunks), chunks_iterator)


if __name__ == '__main__':

    import socketserver
    from pyicap import ICAPServer

    class ThreadingSimpleServer(socketserver.ThreadingMixIn, ICAPServer):
        pass


    server = ThreadingSimpleServer(('127.0.0.1', 1344), ICAPHandler)
    try:
        while True:
            server.handle_request()
    except KeyboardInterrupt:
        print("Finished")
