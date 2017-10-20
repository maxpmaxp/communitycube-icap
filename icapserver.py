# -*- coding: utf8 -*-

from pyicap import BaseICAPRequestHandler


class ICAPHandler(BaseICAPRequestHandler):

    version = "v0.1a"
    ignore_files = ('gif', 'jpg', 'png', 'jpeg', 'txt', 'pdf', 'js', 'exe', 'bin', 'tiff', 'ttf', 'svg',
                    'woff2', 'woff', 'mpeg', 'mp3', 'mp4', 'avi', 'wav', 'aac', 'flac', 'wma', 'vox',
                    'raw', 'dmg', 'webm', 'mkv', 'vob', 'ogg', 'ogv', 'drc', 'gifv', 'mng', 'qt',
                    'wmv', 'yuv', 'rm', 'rmvb', 'asf', 'amv', 'm4p', 'm4v', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv',
                    'm2v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b')

    # Simple echo-style server icap://icap.myorganization.com/echo

    def echo_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('Preview', '0')
        self.set_icap_header('ISTag', self.version)
        self.send_headers(False)

    def echo_RESPMOD(self):
        self.no_adaptation_required()

    # Simple echo-style server icap://icap.myorganization.com/communitycube_menu

    def communitycube_menu_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('ISTag', self.version)
        self.set_icap_header('Preview', '0')
        self.set_icap_header('Transfer-Ignore', ', '.join(self.ignore_files))
        self.set_icap_header('Transfer-Preview', '*')


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
