import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoSetMinimumDisputePeriodTest(CommutoSwapTest.CommutoSwapTest):

    def test_setMinimumDisputePeriod_caller_is_timelock(self):
        #Ensure that the caller of the setMinimumDisputePeriod function is the timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.commuto_swap_contract.functions.setMinimumDisputePeriod(10).transact(tx_details)
            raise Exception("test_setMinimumDisputePeriod_caller_is_timelock: Expected revert not received")
        except ValueError as e:
            #"e79": "Only the current Timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_setMinimumDisputePeriod_event_emission_check(self):
        #Ensure that setting the minimum deposit period emits an event
        MinimumDisputePeriodChanged_filter = self.commuto_swap_contract.events.MinimumDisputePeriodChanged\
            .createFilter(fromBlock="latest")
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.commuto_swap_contract.functions.setMinimumDisputePeriod(10).transact(tx_details)
        events = MinimumDisputePeriodChanged_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["newMinimumDisputePeriod"], 10)