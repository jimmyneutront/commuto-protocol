import cgi
from http.server import BaseHTTPRequestHandler
from InterfaceCommutoSwapTest import InterfaceCommutoSwapTest
import json
from urllib.parse import urlparse, parse_qsl
from uuid import UUID
from web3 import Web3


class CommutoInterfaceTestingServer(BaseHTTPRequestHandler):
    # A dictionary mapping addresses to InterfaceCommutoSwapTest objects which are created during HTTP request handling
    # and are retained for later use.
    interfaceCommutoSwapTests = {}

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
                offer_id, offer_cancellation_transaction_hash = commuto_swap_test\
                    .testBlockchainServiceListenOfferOpenedCanceled()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "offerId": str(offer_id),
                    "offerCancellationTransactionHash": offer_cancellation_transaction_hash.hex()
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-opened-edited':
                offer_id = commuto_swap_test.testBlockchainServiceListenOfferOpenedEdited()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "offerId": str(offer_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-opened-taken-swapFilled':
                swap_id = commuto_swap_test.testBlockchainServiceListenSwapFilled()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "swapID": str(swap_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-opened-taken-SwapFilled-PaymentSent':
                swap_id = commuto_swap_test.testBlockchainServiceListenPaymentSent()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "swapID": str(swap_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-opened-taken-SwapFilled-PaymentSent-Received':
                swap_id = commuto_swap_test.testBlockchainServiceListenPaymentReceived()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "swapID": str(swap_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-opened-taken-SwapFilled-PaymentSent-Received-BuyerClosed':
                swap_id = commuto_swap_test.testBlockchainServiceListenBuyerClosed()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "swapID": str(swap_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-opened-taken-SwapFilled-PaymentSent-Received-SellerClosed':
                swap_id = commuto_swap_test.testBlockchainServiceListenSellerClosed()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "swapID": str(swap_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-opened-taken-DisputeRaised':
                swap_id = commuto_swap_test.testBlockchainServiceListenDisputeRaised()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "swapID": str(swap_id),
                    "disputeAgent0": commuto_swap_test.dispute_agent_0,
                    "disputeAgent1": commuto_swap_test.dispute_agent_1,
                    "disputeAgent2": commuto_swap_test.dispute_agent_2,
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_blockchainservice_handleFailedTransaction'):
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            transaction_hash = commuto_swap_test.testBlockchainServiceHandleFailedTransaction()
            response = {
                "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                "transactionHash": transaction_hash.hex()
            }
            self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_blockchainservice_handleLongPendingOrDroppedTransaction'):
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            response = {
                "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address)
            }
            self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_blockchainservice_getServiceFeeRate'):
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            response = {
                "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
            }
            self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_handleOfferOpenedEvent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            if params['events'] == 'offer-opened':
                offer_id = commuto_swap_test.testOfferServiceHandleOfferOpenedEvent()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "offerId": str(offer_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_forUserIsMakerOffer_handleOfferOpenedEvent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            offerID = UUID(params['offerID'])
            if params['events'] == 'offer-opened' and offerID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testOfferServiceHandleOfferOpenedEventForUserIsMakerOffer(
                    offerID
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_handleOfferEditedEvent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            if params['events'] == 'offer-opened-edited':
                offer_id = commuto_swap_test.testBlockchainServiceListenOfferOpenedEdited()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "offerId": str(offer_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_handleOfferCanceledEvent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            if params['events'] == 'offer-opened':
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                self.interfaceCommutoSwapTests[commuto_swap_test.commuto_swap_contract.address] = commuto_swap_test
                offer_id = commuto_swap_test.testOfferServiceHandleOfferOpenedEvent()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "offerId": str(offer_id),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
            elif params['events'] == 'offer-canceled':
                address = Web3.toChecksumAddress(params['commutoSwapAddress'])
                offer_cancellation_transaction_hash = self.interfaceCommutoSwapTests[address]\
                    .testOfferServiceHandleOfferCanceledEvent()
                response = {
                    "offerCancellationTransactionHash": offer_cancellation_transaction_hash.hex()
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_handleOfferTakenEvent'):
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
        elif self.path.__contains__('/test_offerservice_forUserIsMaker_handleOfferTakenEvent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            offerID = UUID(params['offerID'])
            makerInterfaceIDString = params['interfaceID']
            if params['events'] == 'offer-opened-taken' and offerID is not None and makerInterfaceIDString is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testOfferServiceHandleOfferTakenEventForUserIsMaker(
                    offer_id=offerID,
                    maker_interface_id_string=makerInterfaceIDString.replace(' ', '+'),
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_forUserIsTaker_handleOfferTakenEvent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            offerID = UUID(params['offerID'])
            makerInterfaceIDString = params['makerInterfaceID']
            takerInterfaceIDString = params['takerInterfaceID']
            if params['events'] == 'offer-opened-taken' and offerID is not None and makerInterfaceIDString is not None \
                    and takerInterfaceIDString is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                '''
                The Base64-encoded interface IDs may contain pluses, which parse_qsl interprets as encoded space 
                characters, so replace any spaces with +.
                '''
                commuto_swap_test.testBlockchainServiceListenOfferOpenedTaken(
                    offerID,
                    makerInterfaceIDString.replace(' ', '+'),
                    takerInterfaceIDString.replace(' ', '+'),
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_handleServiceFeeRateChangedEvent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            if params['events'] == 'ServiceFeeRateChanged':
                commuto_swap_test.testOfferServiceHandleServiceFeeRateChangedEvent()
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address)
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_openOffer'):
            self.set_headers()
            commuto_swap_test = InterfaceCommutoSwapTest()
            commuto_swap_test.setUp()
            response = {
                "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                "stablecoinAddress": str(commuto_swap_test.test_dai_contract.address)
            }
            self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_cancelOffer') or self.path \
                .__contains__('/test_offerservice_editOffer'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            offerID = UUID(params['offerID'])
            if params['events'] == 'offer-opened' and offerID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testOfferServiceCancelOffer(
                    offerID
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_offerservice_takeOffer'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            offerID = UUID(params['offerID'])
            settlement_method_string = params['settlement_method_string']
            if params['events'] == 'offer-opened' and offerID is not None and settlement_method_string is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testOfferServiceTakeOffer(
                    offerID,
                    settlement_method_string,
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "stablecoinAddress": str(commuto_swap_test.test_dai_contract.address)
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_swapservice_handleNewSwap'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            offerID = UUID(params['offerID'])
            if params['events'] == 'offer-opened-taken' and offerID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testOfferServiceHandleOfferTakenEventForUserIsMaker(
                    offer_id=offerID,
                    maker_interface_id_string='',
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_swapservice_fillSwap'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            swapID = UUID(params['swapID'])
            if params['events'] == 'offer-opened-taken' and swapID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testSwapServiceFillSwap(
                    swap_id=swapID,
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "stablecoinAddress": str(commuto_swap_test.test_dai_contract.address)
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('/test_swapservice_reportPaymentSent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            swapID = UUID(params['swapID'])
            if params['events'] == 'offer-opened-taken' and swapID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testSwapServiceReportPaymentSent(
                    swap_id=swapID,
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "stablecoinAddress": str(commuto_swap_test.test_dai_contract.address)
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('test_swapservice_reportPaymentReceived'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            swapID = UUID(params['swapID'])
            if params['events'] == 'offer-opened-taken-PaymentSent' and swapID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testSwapServiceReportPaymentReceived(
                    swap_id=swapID,
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "stablecoinAddress": str(commuto_swap_test.test_dai_contract.address)
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('test_swapservice_closeSwap'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            swapID = UUID(params['swapID'])
            if params['events'] == 'offer-opened-taken-PaymentSent-Received' and swapID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testSwapServiceCloseSwap(
                    swap_id=swapID,
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "stablecoinAddress": str(commuto_swap_test.test_dai_contract.address)
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('test_disputeservice_raiseDispute'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            swapID = UUID(params['swapID'])
            if params['events'] == 'offer-opened-taken' and swapID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testDisputeServiceRaiseDispute(
                    swap_id=swapID,
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "stablecoinAddress": str(commuto_swap_test.test_dai_contract.address)
                }
                self.wfile.write(bytes(json.dumps(response).encode()))
        elif self.path.__contains__('test_disputeservice_handleDisputeRaisedEvent'):
            query = urlparse(self.path).query
            params = dict(parse_qsl(query))
            self.set_headers()
            swapID = UUID(params['swapID'])
            if params['events'] == 'offer-opened-taken-DisputeRaised' and swapID is not None:
                commuto_swap_test = InterfaceCommutoSwapTest()
                commuto_swap_test.setUp()
                commuto_swap_test.testDisputeServiceHandleDisputeRaisedEvent(
                    swap_id=swapID,
                )
                response = {
                    "commutoSwapAddress": str(commuto_swap_test.commuto_swap_contract.address),
                    "stablecoinAddress": str(commuto_swap_test.test_dai_contract.address)
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
