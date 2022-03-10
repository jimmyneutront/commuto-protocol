import CommutoSwapTest
from hexbytes import HexBytes
from time import sleep
from uuid import uuid4

# Note: this should probably be moved to a CommutoEscalateDisputeTest file
# TODO: Ensure escalation can only be done by maker or taker
# TODO: Ensure disputed swap can't be escalated for lack of agreement if dispute agents are in agreement
# TODO: Ensure disputed swap can only be escalated to token holders given nonmatching response from dispute agents if > 1 week has passed
# TODO: Ensure disputed swap can't be escalated given lack of maker response if maker has responded
# TODO: Ensure disputed swap can only be escalated to token holders given lack of response from maker if > 1 week has passed
# TODO: Ensure disputed swap can't be escalated given lack of taker response if taker has responded
# TODO: Ensure disputed swap can only be escalated to token holders given lack of response from taker if > 1 week has passed
# TODO: Ensure disputed swap can't be escalated for rejection if resolution proposal wasn't rejected
# TODO: Ensure dispute escalation emits event

# TODO: Immediately escalate swap upon rejection

class CommutoEscalateDisputeTest(CommutoSwapTest.CommutoSwapTest):

    def test_escalateDispute_caller_is_maker_or_taker(self):
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
                "disputeRaiser": 0,
            }
            self.test_dai_contract.functions.increaseAllowance(
                self.commuto_swap_deployment_tx_receipt.contractAddress,
                11,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.takeOffer(
                newOfferID,
                newSwap,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.raiseDispute(
                newOfferID,
                self.dispute_agent_0,
                self.dispute_agent_1,
                self.dispute_agent_2
            ).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_0
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 11, 9, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_2
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 9, 11, 0).transact(tx_details)
            sleep(7)
            self.commuto_swap_contract.functions.escalateDispute(newOfferID, 1).transact(tx_details)
        except ValueError as e:
            #"e75": "Only maker or taker can escalate disputed swap"
            if not "e75" in str(e):
                raise e