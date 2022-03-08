import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoDisputeTest(CommutoSwapTest.CommutoSwapTest):

    def test_raiseDispute_swap_existence_check(self):
        #Ensure raiseDispute checks for swap existence
        try:
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.raiseDispute(
                uuid4().bytes,
                self.dispute_agent_0,
                self.dispute_agent_1,
                self.dispute_agent_2
            ).transact(tx_details)
            raise (Exception("test_raiseDispute_swap_existence_check failed without raising exception"))
        except ValueError as e:
            # "e33": "A swap with the specified id does not exist"
            if not "e33" in str(e):
                raise e

    def test_raiseDispute_dispute_agents_active_check(self):
        #Ensure raiseDispute checks that selected dispute agents are active
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
                "from": self.dispute_agent_0
            }
            self.commuto_swap_contract.functions.raiseDispute(
                newOfferID,
                self.dispute_agent_0,
                self.dispute_agent_1,
                self.maker_address
            ).transact(tx_details)
            raise (Exception("test_raiseDispute_dispute_agents_active_check failed without raising exception"))
        except ValueError as e:
            # "e3": "Selected dispute agents must be active"
            if not "e3" in str(e):
                raise e

    def test_raiseDispute_caller_is_maker_or_taker_check(self):
        #Ensure raiseDispute can only be called by the maker or taker
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
                "from": self.dispute_agent_0
            }
            self.commuto_swap_contract.functions.raiseDispute(
                newOfferID,
                self.dispute_agent_0,
                self.dispute_agent_1,
                self.dispute_agent_2
            ).transact(tx_details)
            raise (Exception("test_raiseDispute_caller_is_maker_or_taker_check failed without raising exception"))
        except ValueError as e:
            # "e44": "Only swap maker or taker can call this function"
            if not "e44" in str(e):
                raise e

    # TODO: Ensure event is emitted when dispute is raised
    # TODO: Ensure dispute can't be raised if maker has closed
    # TODO: Ensure dispute can't be raised if taker has closed
    # TODO: Ensure swap can't be filled if swap is disputed
    # TODO: Ensure payment can't be reported as sent if swap is disputed
    # TODO: Ensure payment can't be reported as received if swap is disputed
    # TODO: Ensure swap can't be closed if swap is disputed
    # TODO: Ensure resolution proposals can only be submitted by dispute agents
    # TODO: Ensure total payout amount in resolution proposals equals total amount locked in escrow, minus service fee
    # TODO: Ensure disputed swap can only be paid out if both maker and taker agree
    # TODO: Ensure disputed swap can only be escalated to token holders given nonmatching response from dispute agents if > 1 week has passed
    # TODO: Ensure disputed swap can only be escalated to token holders given lack of response from maker if > 1 week has passed
    # TODO: Ensure disputed swap can only be escalated to token holders given lack of response from taker if > 1 week has passed
