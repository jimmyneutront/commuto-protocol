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

    def test_changeTimelock_event_emission_check(self):
        #Ensure that changeTimelock emits TimelockChanged event upon successful change
        TimelockChanged_event_filter = self.commuto_swap_contract.events.TimelockChanged\
            .createFilter(fromBlock="latest")
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.commuto_swap_contract.functions.changeTimelock(self.Timelock_contract.address).transact(tx_details)
        events = TimelockChanged_event_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["oldTimelock"], self.w3.eth.accounts[2])
        self.assertEqual(events[0]["args"]["newTimelock"], self.Timelock_contract.address)