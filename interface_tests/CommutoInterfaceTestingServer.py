from http.server import BaseHTTPRequestHandler
from InterfaceCommutoSwapTest import InterfaceCommutoSwapTest
import json


class CommutoInterfaceTestingServer(BaseHTTPRequestHandler):
    def set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path.endswith('/test_blockchainservice_listen'):
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            commuto_swap_test.testBlockchainServiceListen()
            response = {
                "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
            }
            self.wfile.write(bytes(json.dumps(response).encode()))
