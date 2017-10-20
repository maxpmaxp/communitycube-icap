# -*- coding: utf8 -*-

from pyicap import BaseICAPRequestHandler


class ICAPHandler(BaseICAPRequestHandler):

    istag = "v0.1"

    # Simple echo-style server icap://icap.myorganization.com/echo

    def echo_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('Preview', '0')
        self.set_icap_header('ISTag', self.istag)
        self.send_headers(False)

    def echo_RESPMOD(self):
        self.no_adaptation_required()

    # Simple echo-style server icap://icap.myorganization.com/communitycube_menu

    def communitycube_menu_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('ISTag', self.istag)
        self.set_icap_header('Preview', '0')
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
