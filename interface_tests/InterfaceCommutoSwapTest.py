import base64
from uuid import uuid4, UUID
from hexbytes import HexBytes
from tests.CommutoSwapTest import CommutoSwapTest


class InterfaceCommutoSwapTest(CommutoSwapTest):

    def testBlockchainServiceListenOfferOpenedTaken(
            self,
            offer_id: UUID = uuid4(),
            maker_interface_id_string: str = base64.b64encode('maker interface Id here'.encode('utf8')).decode('ascii'),
            taker_interface_id_string: str = base64.b64encode('taker interface Id here'.encode('utf8')).decode('ascii'),
    ):
        maker_as_seller_swap_id = offer_id
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_seller_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": base64.b64decode(s = maker_interface_id_string + '=='),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(maker_as_seller_swap_id.bytes),
            maker_as_seller_offer
        ).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        maker_as_seller_swap = {
            "isCreated": False,
            "requiresFill": True,
            "maker": self.maker_address,
            "makerInterfaceId": base64.b64decode(s = maker_interface_id_string),
            "taker": self.taker_address,
            "takerInterfaceId": base64.b64decode(s = taker_interface_id_string),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "takenSwapAmount": 10000,
            "serviceFeeAmount": 100,
            "serviceFeeRate": 100,
            "direction": 1,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethod": "USD-SWIFT|a price here".encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100
        ).transact(tx_details)
        self.commuto_swap_contract.functions.takeOffer(
            HexBytes(maker_as_seller_swap_id.bytes),
            maker_as_seller_swap,
        ).transact(tx_details)

        return maker_as_seller_swap_id

    def testBlockchainServiceListenOfferOpenedCanceled(self):
        maker_as_seller_swap_id = uuid4()
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_seller_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": HexBytes("maker interface Id here".encode("utf-8").hex()),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(maker_as_seller_swap_id.bytes),
            maker_as_seller_offer
        ).transact(tx_details)
        self.commuto_swap_contract.functions.cancelOffer(
            HexBytes(maker_as_seller_swap_id.bytes),
        ).transact(tx_details)

        return maker_as_seller_swap_id

    def testBlockchainServiceListenOfferOpenedEdited(self):
        maker_as_seller_swap_id = uuid4()
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_seller_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": HexBytes("maker interface Id here".encode("utf-8").hex()),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(maker_as_seller_swap_id.bytes),
            maker_as_seller_offer
        ).transact(tx_details)
        editedOffer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ['{"f":"EUR","p":"SEPA","m":"0.98"}'.encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.commuto_swap_contract.functions.editOffer(
            HexBytes(maker_as_seller_swap_id.bytes),
            editedOffer
        ).transact(tx_details)

        return maker_as_seller_swap_id

    def testBlockchainServiceListenSwapFilled(self) -> uuid4:
        maker_as_seller_swap_id = uuid4()
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_seller_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ['{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            maker_as_seller_swap_id.bytes,
            maker_as_seller_offer
        ).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        maker_as_seller_swap = {
            "isCreated": True,
            "requiresFill": True,
            "maker": self.maker_address,
            "makerInterfaceId": bytes(),
            "taker": self.taker_address,
            "takerInterfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "takenSwapAmount": 10000,
            "serviceFeeAmount": 100,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethod": '{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": False,
            "isPaymentReceived": False,
            "hasBuyerClosed": False,
            "hasSellerClosed": False,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100
        ).transact(tx_details)
        self.commuto_swap_contract.functions.takeOffer(
            maker_as_seller_swap_id.bytes,
            maker_as_seller_swap,
        ).transact(tx_details)
        tx_details = {
            "from": self.maker_address,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            10000
        ).transact(tx_details)
        self.commuto_swap_contract.functions.fillSwap(
            maker_as_seller_swap_id.bytes,
        ).transact(tx_details)

        return maker_as_seller_swap_id

    def testBlockchainServiceListenPaymentSent(self) -> uuid4:
        maker_as_buyer_swap_id = uuid4()
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_buyer_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethods": ['{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            maker_as_buyer_swap_id.bytes,
            maker_as_buyer_offer
        ).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        maker_as_buyer_swap = {
            "isCreated": True,
            "requiresFill": False,
            "maker": self.maker_address,
            "makerInterfaceId": bytes(),
            "taker": self.taker_address,
            "takerInterfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "takenSwapAmount": 10000,
            "serviceFeeAmount": 100,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethod": '{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": False,
            "isPaymentReceived": False,
            "hasBuyerClosed": False,
            "hasSellerClosed": False,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11100
        ).transact(tx_details)
        self.commuto_swap_contract.functions.takeOffer(
            maker_as_buyer_swap_id.bytes,
            maker_as_buyer_swap,
        ).transact(tx_details)
        tx_details = {
            "from": self.maker_address,
        }
        self.commuto_swap_contract.functions.reportPaymentSent(
            maker_as_buyer_swap_id.bytes
        ).transact(tx_details)

        return maker_as_buyer_swap_id

    def testOfferServiceHandleOfferOpenedEvent(self):
        self.maker_as_seller_swap_id = uuid4()
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_seller_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": "maker interface Id here".encode("utf-8"),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ['{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(self.maker_as_seller_swap_id.bytes),
            maker_as_seller_offer
        ).transact(tx_details)

        return self.maker_as_seller_swap_id

    def testOfferServiceHandleOfferOpenedEventForUserIsMakerOffer(self, offer_id: UUID, interface_id: str):
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_seller_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": base64.b64decode(s = interface_id + '=='),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(offer_id.bytes),
            maker_as_seller_offer
        ).transact(tx_details)

    def testOfferServiceHandleOfferCanceledEvent(self):
        tx_details = {
            "from": self.maker_address,
        }
        self.commuto_swap_contract.functions.cancelOffer(
            HexBytes(self.maker_as_seller_swap_id.bytes),
        ).transact(tx_details)

    def testOfferServiceHandleServiceFeeRateChangedEvent(self):
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.commuto_swap_contract.functions.setServiceFeeRate(200).transact(tx_details)

    def testOfferServiceCancelOffer(self, offer_id):
        # We are using the taker address for this test, since that is the address used by interface testing code
        tx_details = {
            "from": self.taker_address,
        }
        # For this test, the maker uses taker_address
        maker_as_buyer_offer = {
            "isCreated": True,
            "isTaken": False,
            "maker": self.maker_address,
            "interfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(offer_id.bytes),
            maker_as_buyer_offer
        ).transact(tx_details)

    def testOfferServiceTakeOffer(self, offer_id, settlement_method_string: str):
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_buyer_offer = {
            "isCreated": True,
            "isTaken": False,
            "maker": self.maker_address,
            "interfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10_000_000_000_000_000_000_000,
            "amountUpperBound": 20_000_000_000_000_000_000_000,
            "securityDepositAmount": 2_000_000_000_000_000_000_000,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethods": [settlement_method_string.encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            2_200_000_000_000_000_000_000,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(offer_id.bytes),
            maker_as_buyer_offer
        ).transact(tx_details)

    def testOfferServiceHandleOfferTakenEventForUserIsMaker(self, offer_id: UUID, maker_interface_id_string: str):
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_buyer_offer = {
            "isCreated": True,
            "isTaken": False,
            "maker": self.maker_address,
            "interfaceId": base64.b64decode(s = maker_interface_id_string + '=='),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethods": ['{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(offer_id.bytes),
            maker_as_buyer_offer
        ).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        maker_as_buyer_swap = {
            "isCreated": False,
            "requiresFill": True,
            "maker": self.maker_address,
            "makerInterfaceId": base64.b64decode(s = maker_interface_id_string + '=='),
            "taker": self.taker_address,
            "takerInterfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "takenSwapAmount": 10000,
            "serviceFeeAmount": 100,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethod": '{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11100
        ).transact(tx_details)
        self.commuto_swap_contract.functions.takeOffer(
            offer_id.bytes,
            maker_as_buyer_swap,
        ).transact(tx_details)

    def testSwapServiceFillSwap(self, swap_id: UUID):
        tx_details = {
            # The account used by interfaces during tests
            "from": self.w3.eth.accounts[1],
        }
        maker_as_seller_offer = {
            "isCreated": True,
            "isTaken": False,
            "maker": self.w3.eth.accounts[1],
            "interfaceId":bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ['{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"), ],
            "protocolVersion": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            HexBytes(swap_id.bytes),
            maker_as_seller_offer
        ).transact(tx_details)
        maker_as_seller_swap = {
            "isCreated": False,
            "requiresFill": True,
            "maker": self.w3.eth.accounts[1],
            "makerInterfaceId": bytes(),
            "taker": self.w3.eth.accounts[0],
            "takerInterfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "takenSwapAmount": 10000,
            "serviceFeeAmount": 100,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethod": '{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"),
            "protocolVersion": 0,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11100
        ).transact(tx_details)
        self.commuto_swap_contract.functions.takeOffer(
            swap_id.bytes,
            maker_as_seller_swap,
        ).transact(tx_details)

    def testSwapServiceReportPaymentSent(self, swap_id: UUID):
        tx_details = {
            # The account used by interfaces during tests
            "from": self.w3.eth.accounts[1],
        }
        maker_as_buyer_offer = {
            "isCreated": True,
            "isTaken": False,
            "maker": self.w3.eth.accounts[1],
            "interfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethods": ['{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"), ],
            "protocolVersion": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            swap_id.bytes,
            maker_as_buyer_offer
        ).transact(tx_details)
        tx_details = {
            "from": self.w3.eth.accounts[0],
        }
        maker_as_seller_swap = {
            "isCreated": False,
            "requiresFill": True,
            "maker": self.w3.eth.accounts[1],
            "makerInterfaceId": bytes(),
            "taker": self.w3.eth.accounts[0],
            "takerInterfaceId": bytes(),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "takenSwapAmount": 10000,
            "serviceFeeAmount": 100,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethod": '{"f":"USD","p":"SWIFT","m":"1.00"}'.encode("utf-8"),
            "protocolVersion": 0,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11100
        ).transact(tx_details)
        self.commuto_swap_contract.functions.takeOffer(
            swap_id.bytes,
            maker_as_seller_swap,
        ).transact(tx_details)
