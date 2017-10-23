# -*- coding: utf8 -*-

import logging

from pyicap import BaseICAPRequestHandler


class ICAPHandler(BaseICAPRequestHandler):

    preview_size = b'512'
    _server_version = 'CommunitycubeICAP/0.1a'

    ignore_files = (b'gif', b'jpg', b'png', b'jpeg', b'txt', b'pdf', b'js', b'exe', b'bin', b'tiff', b'ttf', b'svg',
                    b'woff2', b'woff', b'mpeg', b'mp3', b'mp4', b'avi', b'wav', b'aac', b'flac', b'wma', b'vox',
                    b'raw', b'dmg', b'webm', b'mkv', b'vob', b'ogg', b'ogv', b'drc', b'gifv', b'mng', b'qt',
                    b'wmv', b'yuv', b'rm', b'rmvb', b'asf', b'amv', b'm4p', b'm4v', b'mpg', b'mp2', b'mpeg', b'mpe',
                    b'mpv', b'm2v', b'svi', b'3gp', b'3g2', b'mxf', b'roq', b'nsv', b'flv', b'f4v', b'f4p', b'f4a',
                    b'f4b')

    # Simple echo-style server icap://icap.myorganization.com/communitycube_menu

    @property
    def res_status_code(self):
        try:
            status = int(self.enc_res_status[1])
        except Exception:
            logging.warning('Unexpected status line: {}'.format(str(self.enc_res_status)))
            status = None
        return status

    @property
    def res_content_type(self):
        ct_headers = self.enc_res_headers.get(b'content-type')
        if ct_headers:
            if len(ct_headers) > 1:
                logging.warning("Too many content-type headers: {}".format(ct_headers))
            return ct_headers[0]

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

    def send_modified_content(self, head):
        self.set_icap_response(200)

        if self.enc_res_status is not None:
            self.set_enc_status(b' '.join(self.enc_res_status))
        for h in self.enc_res_headers:
            for v in self.enc_res_headers[h]:
                self.set_enc_header(h, v)

        self.send_headers(True)

        # Send modified head
        self.write_chunk(head)

        if self.ieof:
            # All content was within the preview
            self.write_chunk(b'')
        else:
            # Send unread tail
            self.cont()
            while True:
                chunk = self.read_chunk()
                self.write_chunk(chunk)
                if chunk == b'':
                    break


    def communitycube_menu_RESPMOD(self):
        if not self.is_adaptation_required():
            self.no_adaptation_required()
            return

        was_modified = False
        if self.preview:
            chunk = self.read_chunk()
            tag = b'<head>'
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
            try:
                i_tag_end = chunk.index(tag) + len(tag)
                chunk = chunk[:i_tag_end] + injection + chunk[i_tag_end:]
                self.send_modified_content(chunk)
            except ValueError:
                pass

        if not was_modified:
            self.no_adaptation_required()


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
