from http.server import HTTPServer
import IOSTestingServer


def run_ios_test():
    server_address = ('localhost', 8546)
    server = HTTPServer(server_address, IOSTestingServer.IOSTestingServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


run_ios_test()
