import CommutoSwapTest

class CommutoSwapChangeTimelockTest(CommutoSwapTest.CommutoSwapTest):

    def test_changeTimelock_caller_is_timelock(self):
        #Ensure that changeTimelock cannot be called by any account other than the timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.commuto_swap_contract.functions.changeTimelock(
                self.w3.eth.accounts[2],
            ).transact(tx_details)
            raise Exception("test_changeTimelock_caller_is_timelock: Expected revert not received")
        except ValueError as e:
            # "e79": "Only the current Timelock can call this function"
            if not "e79" in str(e):
                raise e