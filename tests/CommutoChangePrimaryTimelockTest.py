import CommutoSwapTest

class CommutoChangePrimaryTimelockTest(CommutoSwapTest.CommutoSwapTest):

    def test_changePrimaryTimelock_caller_is_primary_timelock(self):
        #Ensure that changePrimaryTimelock cannot be called by any account other than the primary timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.commuto_swap_contract.functions.changePrimaryTimelock(
                self.w3.eth.accounts[2],
            ).transact(tx_details)
            raise Exception("test_changeTimelock_caller_is_primary_timelock: Expected revert not received")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_changePrimaryTimelock_event_emission_check(self):
        #Ensure that changePrimaryTimelock emits PrimaryTimelockChanged event upon successful change
        PrimaryTimelockChanged_event_filter = self.commuto_swap_contract.events.PrimaryTimelockChanged\
            .createFilter(fromBlock="latest")
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.commuto_swap_contract.functions.changePrimaryTimelock(self.primary_timelock_contract.address)\
            .transact(tx_details)
        events = PrimaryTimelockChanged_event_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["oldPrimaryTimelock"], self.w3.eth.accounts[2])
        self.assertEqual(events[0]["args"]["newPrimaryTimelock"], self.primary_timelock_contract.address)