import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

#Note: this should probably be moved to a CommutoProposeResolutionTest file
    # TODO: Ensure resolution proposals can only be submitted by dispute agents assigned to swap
    # TODO: Ensure total payout amount in resolution proposals must equal total amount locked in escrow, minus service fee
    # TODO: Ensure resolution proposal can't be submitted if the maker or taker has already accepted or rejected
    # TODO: Ensure proposing resolution emits event

class CommutoProposeResolutionTest(CommutoSwapTest.CommutoSwapTest):

    def test_proposeResolution_swap_is_disputed_check(self):
        #Ensure that a resolution can't be proposed for a swap that isn't disputed or doesn't exist
        try:
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.proposeResolution(uuid4().bytes, 0, 0, 0).transact(tx_details)
            raise (Exception("test_proposeResolution_swap_is_disputed_check failed without raising exception"))
        except ValueError as e:
            # "e54": "Swap doesn't exist or isn't disputed"
            if not "e54" in str(e):
                raise e