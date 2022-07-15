from uuid import uuid4
from hexbytes import HexBytes
from tests.CommutoSwapTest import CommutoSwapTest


class InterfaceCommutoSwapTest(CommutoSwapTest):

    def testBlockchainServiceListenOfferOpenedTaken(self):
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
        tx_details = {
            "from": self.taker_address
        }
        maker_as_seller_swap = {
            "isCreated": False,
            "requiresFill": True,
            "maker": self.maker_address,
            "makerInterfaceId": HexBytes("maker interface Id here".encode("utf-8").hex()),
            "taker": self.taker_address,
            "takerInterfaceId": HexBytes("taker interface Id here".encode("utf-8").hex()),
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
            "settlementMethods": ["EUR-SEPA|an edited price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.commuto_swap_contract.functions.editOffer(
            HexBytes(maker_as_seller_swap_id.bytes),
            editedOffer
        ).transact(tx_details)

        return maker_as_seller_swap_id

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
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
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

    def testOfferServiceHandleOfferCanceledEvent(self):
        tx_details = {
            "from": self.maker_address,
        }
        self.commuto_swap_contract.functions.cancelOffer(
            HexBytes(self.maker_as_seller_swap_id.bytes),
        ).transact(tx_details)