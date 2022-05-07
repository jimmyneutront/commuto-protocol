import CommutoSwapTest

class CommutoTokenTest(CommutoSwapTest.CommutoSwapTest):

    def test_changeTimelock_caller_is_timelock(self):
        #Ensure that changeTimelock cannot be called by any account other than Timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.CommutoToken_contract.functions.changeTimelock(
                self.w3.eth.accounts[2],
            ).transact(tx_details)
            raise Exception("test_changeTimelock_caller_is_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_changeTimelock_event_emission_check(self):
        #Ensure that changeTimelock emits TimelockChanged event upon successful change
        TimelockChanged_filter = self.CommutoToken_contract.events.TimelockChanged.createFilter(fromBlock="latest")
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.CommutoToken_contract.functions.changeTimelock(self.primary_timelock_contract.address).transact(tx_details)
        events = TimelockChanged_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["oldTimelock"], self.w3.eth.accounts[2])
        self.assertEqual(events[0]["args"]["newTimelock"], self.primary_timelock_contract.address)

    def test_mint_caller_is_primary_timelock(self):
        #Ensure that mint cannot be called by any account other than the primary timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.CommutoToken_contract.functions.mint(
                self.w3.eth.accounts[2],
                100,
            ).transact(tx_details)
            raise Exception("test_mint_caller_is_primary_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_burn_caller_is_primary_timelock(self):
        #Ensure that burn cannot be called by any account other than the primary timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.CommutoToken_contract.functions.burn(
                self.w3.eth.accounts[2],
                100,
            ).transact(tx_details)
            raise Exception("test_burn_caller_is_primary_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            if not "e79" in str(e):
                raise e