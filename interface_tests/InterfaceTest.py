from http.server import HTTPServer
import CommutoInterfaceTestingServer


def run_interface_test_server():
    server_address = ('localhost', 8546)
    server = HTTPServer(server_address, CommutoInterfaceTestingServer.CommutoInterfaceTestingServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


run_interface_test_server()
