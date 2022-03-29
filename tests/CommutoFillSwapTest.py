import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoFillSwapTest(CommutoSwapTest.CommutoSwapTest):

    def test_fillSwap_swap_existence_check(self):
        #Ensure fillSwap checks for swap existence
        try:
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.fillSwap(
                HexBytes(uuid4().bytes)
            ).transact(tx_details)
            raise (Exception("test_fillSwap_swap_existence_check failed without raising exception"))
        except ValueError as e:
            # "e33": "A swap with the specified id does not exist"
            if not "e33" in str(e):
                raise e

    def test_fillSwap_caller_is_maker_and_seller_check(self):
        #Ensure fillSwap can only be called by maker and seller
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
                "amountLowerBound": 10000,
                "amountUpperBound": 10000,
                "securityDepositAmount": 1000,
                "serviceFeeRate": 100,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                1100,
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
                "amountLowerBound": 10000,
                "amountUpperBound": 10000,
                "securityDepositAmount": 1000,
                "takenSwapAmount": 10000,
                "serviceFeeAmount": 100,
                "serviceFeeRate": 100,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethod": "USD-SWIFT".encode("utf-8"),
                "protocolVersion": 1,
                "isPaymentSent": True,
                "isPaymentReceived": True,
                "hasBuyerClosed": True,
                "hasSellerClosed": True,
                "disputeRaiser": 0,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                1100,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.takeOffer(
                newOfferID,
                newSwap,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.fillSwap(
                newOfferID
            ).transact(tx_details)
            raise (Exception("test_fillSwap_caller_is_maker_and_seller_check failed without raising exception"))
        except ValueError as e:
            # "e47": "Only maker and seller can fill swap"
            if not "e47" in str(e):
                raise e

    def test_fillSwap_swap_requires_filling_check(self):
        #Ensure fillSwap can only be called on swaps that require filling
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
                "amountLowerBound": 10000,
                "amountUpperBound": 10000,
                "securityDepositAmount": 1000,
                "serviceFeeRate": 100,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                1100,
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
                "amountLowerBound": 10000,
                "amountUpperBound": 10000,
                "securityDepositAmount": 1000,
                "takenSwapAmount": 10000,
                "serviceFeeAmount": 100,
                "serviceFeeRate": 100,
                "direction": 1,
                "price": HexBytes("a price here".encode("utf-8").hex()),
                "settlementMethod": "USD-SWIFT".encode("utf-8"),
                "protocolVersion": 1,
                "isPaymentSent": True,
                "isPaymentReceived": True,
                "hasBuyerClosed": True,
                "hasSellerClosed": True,
                "disputeRaiser": 0,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                1100,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.takeOffer(
                newOfferID,
                newSwap,
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                10000,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.fillSwap(
                newOfferID
            ).transact(tx_details)
            self.commuto_swap_contract.functions.fillSwap(
                newOfferID
            ).transact(tx_details)
            raise (Exception("test_fillSwap_swap_requires_filling_check failed without raising exception"))
        except ValueError as e:
            # "e18": "Swap does not require filling"
            if not "e18" in str(e):
                raise e

    #TODO: More fillSwap tests