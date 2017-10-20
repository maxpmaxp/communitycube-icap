# -*- coding: utf8 -*-

from pyicap import BaseICAPRequestHandler


class ICAPHandler(BaseICAPRequestHandler):

    version = b'v0.1a'
    ignore_files = (b'gif', b'jpg', b'png', b'jpeg', b'txt', b'pdf', b'js', b'exe', b'bin', b'tiff', b'ttf', b'svg',
                    b'woff2', b'woff', b'mpeg', b'mp3', b'mp4', b'avi', b'wav', b'aac', b'flac', b'wma', b'vox',
                    b'raw', b'dmg', b'webm', b'mkv', b'vob', b'ogg', b'ogv', b'drc', b'gifv', b'mng', b'qt',
                    b'wmv', b'yuv', b'rm', b'rmvb', b'asf', b'amv', b'm4p', b'm4v', b'mpg', b'mp2', b'mpeg', b'mpe',
                    b'mpv', b'm2v', b'svi', b'3gp', b'3g2', b'mxf', b'roq', b'nsv', b'flv', b'f4v', b'f4p', b'f4a',
                    b'f4b')

    # Simple echo-style server icap://icap.myorganization.com/echo

    def echo_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header(b'Methods', b'RESPMOD')
        self.set_icap_header(b'Preview', b'0')
        self.set_icap_header(b'ISTag', self.version)
        self.send_headers(False)

    def echo_RESPMOD(self):
        self.no_adaptation_required()

    # Simple echo-style server icap://icap.myorganization.com/communitycube_menu

    def communitycube_menu_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header(b'Methods', b'RESPMOD')
        self.set_icap_header(b'ISTag', self.version)
        self.set_icap_header(b'Preview', b'0')
        self.set_icap_header(b'Transfer-Ignore', b', '.join(self.ignore_files))
        self.set_icap_header(b'Transfer-Preview', b'*')
        self.send_headers(False)

    def communitycube_menu_RESPMOD(self):
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
