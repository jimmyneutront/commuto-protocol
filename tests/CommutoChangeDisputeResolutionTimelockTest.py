import CommutoSwapTest

class CommutoChangeDisputeResolutionTimelockTest(CommutoSwapTest.CommutoSwapTest):

    def test_changeDisputeResolutionTimelock_caller_is_primary_timelock(self):
        #Ensure that changeDisputeResolutionTimelock cannot be called by any account other than the primary timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.commuto_swap_contract.functions.changeDisputeResolutionTimelock(
                self.w3.eth.accounts[2],
            ).transact(tx_details)
            raise Exception("test_changeDisputeResolutionTimelock_caller_is_primary_timelock: Expected revert not received")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_changeDisputeResolutionTimelock_event_emission_check(self):
        #Ensure that changeDisputeResolutionTimelock emits DisputeResolutionTimelockChanged event upon successful change
        DisputeResolutionTimelockChanged_event_filter = self.commuto_swap_contract.events\
            .DisputeResolutionTimelockChanged.createFilter(fromBlock="latest")
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.commuto_swap_contract.functions.changeDisputeResolutionTimelock(self.dispute_resolution_timelock_contract.address).transact(tx_details)
        events = DisputeResolutionTimelockChanged_event_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["oldDisputeResolutionTimelock"], self.w3.eth.accounts[2])
        self.assertEqual(events[0]["args"]["newDisputeResolutionTimelock"], self.dispute_resolution_timelock_contract.address)