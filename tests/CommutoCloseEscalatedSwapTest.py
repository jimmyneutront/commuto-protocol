import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoCloseEscalatedSwapTest(CommutoSwapTest.CommutoSwapTest):

    def test_closeEscalatedSwap_caller_is_timelock(self):
        #Ensure the caller of closeEscalatedSwap is the timelock
        try:
            nonExistentOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.w3.eth.accounts[6]
            }
            self.commuto_swap_contract.functions.closeEscalatedSwap(nonExistentOfferID, 1000, 500, 500).transact(tx_details)
        except ValueError as e:
            self.assertTrue("e79" in str(e))