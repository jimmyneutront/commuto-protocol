import cgi
from http.server import BaseHTTPRequestHandler
from InterfaceCommutoSwapTest import InterfaceCommutoSwapTest
import json
from urllib.parse import urlparse, parse_qsl


class CommutoInterfaceTestingServer(BaseHTTPRequestHandler):
    def set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path.__contains__('/test_blockchainservice_listen'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            if params['events'] == 'offer-opened-taken':
                offer_id = commuto_swap_test.testBlockchainServiceListenOfferOpenedTaken()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "offerId": str(offer_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-opened-canceled':
                offer_id = commuto_swap_test.testBlockchainServiceListenOfferOpenedCanceled()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "offerId": str(offer_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))

    # noinspection PyPep8Naming
    def do_POST(self):
        content_type, options_dict = cgi.parse_header(self.headers.get_content_type())
        if content_type != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
        self.set_headers()
        length = int(self.headers['Content-Length'])
        message = json.loads(self.rfile.read(length))
        if type(message) == dict and message["method"] == "net_version":
            response = {
                "id": message['id'],
                "jsonrpc": message["jsonrpc"],
                "result": "31337",  # Hardhat network id
            }
            self.wfile.write(bytes(json.dumps(response).encode()))
