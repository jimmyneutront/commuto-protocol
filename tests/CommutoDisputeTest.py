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

    # TODO: Ensure dispute agents are active
    # TODO: Ensure only maker or taker can raise dispute
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
