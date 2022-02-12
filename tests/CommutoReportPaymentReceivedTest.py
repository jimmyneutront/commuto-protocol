import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoReportPaymentReceivedTest(CommutoSwapTest.CommutoSwapTest):

    def test_reportPaymentReceived_swap_existence_check(self):
        #Ensure reportPaymentReceived checks for swap existence
        try:
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.reportPaymentSent(
                HexBytes(uuid4().bytes)
            ).transact(tx_details)
            raise (Exception("test_reportPaymentReceived_swap_existence_check failed without raising exception"))
        except ValueError as e:
            # "e33":"A swap with the specified id does not exist"
            if not "e33" in str(e):
                raise e

    def test_reportPaymentReceived_payment_sent_check(self):
        #Ensure that reportPaymentReceived requires that payment has been sent
        try:
            newOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address
            }
            newOffer = {
                "isCreated": True,
                "isTaken": True,
                "maker": self.maker_address,
                "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 100,
                "amountUpperBound": 100,
                "securityDepositAmount": 10,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                11,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            newSwap = {
                "isCreated": False,
                "requiresFill": True,
                "maker": self.maker_address,
                "makerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "taker": self.taker_address,
                "takerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 100,
                "amountUpperBound": 100,
                "securityDepositAmount": 10,
                "takenSwapAmount": 100,
                "serviceFeeAmount": 1,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethod": "USD-SWIFT".encode("utf-8"),
                "protocolVersion": 1,
                "isPaymentSent": True,
                "isPaymentReceived": True,
                "hasBuyerClosed": True,
                "hasSellerClosed": True,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                11,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.takeOffer(
                newOfferID,
                newSwap,
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                100,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.fillSwap(
                newOfferID
            ).transact(tx_details)
            self.commuto_swap_contract.functions.reportPaymentReceived(
                newOfferID
            ).transact(tx_details)
            raise (Exception("test_reportPaymentReceived_payment_sent_check failed without raising exception"))
        except ValueError as e:
            # "e37":"Payment sending has not been reported for swap with specified id"
            if not "e37" in str(e):
                raise e

    def test_reportPaymentReceived_duplicate_call_check(self):
        #Ensure reportPaymentReceived cannot be called more than once
        try:
            newOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address,
            }
            newOffer = {
                "isCreated": True,
                "isTaken": True,
                "maker": self.maker_address,
                "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 100,
                "amountUpperBound": 100,
                "securityDepositAmount": 10,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                11,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            newSwap = {
                "isCreated": False,
                "requiresFill": True,
                "maker": self.maker_address,
                "makerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "taker": self.taker_address,
                "takerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 100,
                "amountUpperBound": 100,
                "securityDepositAmount": 10,
                "takenSwapAmount": 100,
                "serviceFeeAmount": 1,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethod": "USD-SWIFT".encode("utf-8"),
                "protocolVersion": 1,
                "isPaymentSent": True,
                "isPaymentReceived": True,
                "hasBuyerClosed": True,
                "hasSellerClosed": True,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                11,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.takeOffer(
                newOfferID,
                newSwap,
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                100,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.fillSwap(
                newOfferID
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address,
            }
            self.commuto_swap_contract.functions.reportPaymentSent(
                newOfferID
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.reportPaymentReceived(
                newOfferID
            ).transact(tx_details)
            self.commuto_swap_contract.functions.reportPaymentReceived(
                newOfferID
            ).transact(tx_details)
            raise (Exception("test_reportPaymentReceived_duplicate_call_check failed without raising exception"))
        except ValueError as e:
            # "e38":"Payment receiving has already been reported for swap with specified id"
            if not "e38" in str(e):
                raise e

    def test_reportPaymentReceived_caller_is_not_maker_buyer_check(self):
        #Ensuring reportPaymentReceived cannot be called by the maker/buyer
        try:
            newOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address,
            }
            newOffer = {
                "isCreated": True,
                "isTaken": True,
                "maker": self.maker_address,
                "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 100,
                "amountUpperBound": 100,
                "securityDepositAmount": 10,
                "direction": 0,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                11,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            newSwap = {
                "isCreated": False,
                "requiresFill": True,
                "maker": self.maker_address,
                "makerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "taker": self.taker_address,
                "takerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 100,
                "amountUpperBound": 100,
                "securityDepositAmount": 10,
                "takenSwapAmount": 100,
                "serviceFeeAmount": 1,
                "direction": 0,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethod": "USD-SWIFT".encode("utf-8"),
                "protocolVersion": 1,
                "isPaymentSent": True,
                "isPaymentReceived": True,
                "hasBuyerClosed": True,
                "hasSellerClosed": True,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                111,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.takeOffer(
                newOfferID,
                newSwap,
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address,
            }
            self.commuto_swap_contract.functions.reportPaymentSent(
                newOfferID
            ).transact(tx_details)
            self.commuto_swap_contract.functions.reportPaymentReceived(
                newOfferID
            ).transact(tx_details)
            raise (Exception("test_reportPaymentReceived_caller_is_not_maker_buyer_check failed without raising "
                             "exception"))
        except ValueError as e:
            # "e39":"Payment receiving can only be reported by seller"
            if not "e39" in str(e):
                raise e

    def test_reportPaymentReceived_caller_is_not_taker_buyer_check(self):
        #Ensure reportPaymentReceived cannot be called by taker/buyer
        try:
            newOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address,
            }
            newOffer = {
                "isCreated": True,
                "isTaken": True,
                "maker": self.maker_address,
                "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 100,
                "amountUpperBound": 100,
                "securityDepositAmount": 10,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                11,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            newSwap = {
                "isCreated": False,
                "requiresFill": True,
                "maker": self.maker_address,
                "makerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "taker": self.taker_address,
                "takerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 100,
                "amountUpperBound": 100,
                "securityDepositAmount": 10,
                "takenSwapAmount": 100,
                "serviceFeeAmount": 1,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethod": "USD-SWIFT".encode("utf-8"),
                "protocolVersion": 1,
                "isPaymentSent": True,
                "isPaymentReceived": True,
                "hasBuyerClosed": True,
                "hasSellerClosed": True,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                11,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.takeOffer(
                newOfferID,
                newSwap,
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                100,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.fillSwap(
                newOfferID
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address,
            }
            self.commuto_swap_contract.functions.reportPaymentSent(
                newOfferID
            ).transact(tx_details)
            self.commuto_swap_contract.functions.reportPaymentReceived(
                newOfferID
            ).transact(tx_details)
            raise (Exception("test_reportPaymentReceived_caller_is_not_taker_buyer_check failed without raising "
                             "exception"))
        except ValueError as e:
            # "e39":"Payment receiving can only be reported by seller"
            if not "e39" in str(e):
                raise e
