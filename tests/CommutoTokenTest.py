import CommutoSwapTest

class CommutoTokenTest(CommutoSwapTest.CommutoSwapTest):

    def test_changeTimelock_caller_is_timelock(self):
        #Ensure that changeTimelock cannot be called by any account other than Timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[2],
            }
            self.CommutoToken_contract.functions.changeTimelock(
                self.w3.eth.accounts[2],
            ).transact(tx_details)
            raise Exception("test_changeTimelock_caller_is_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current Timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_mint_caller_is_timelock(self):
        #Ensure that mint cannot be called by any account other than Timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[2],
            }
            self.CommutoToken_contract.functions.mint(
                self.w3.eth.accounts[2],
                100,
            ).transact(tx_details)
            raise Exception("test_mint_caller_is_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current Timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_burn_caller_is_timelock(self):
        #Ensure that burn cannot be called by any account other than Timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[2],
            }
            self.CommutoToken_contract.functions.burn(
                self.w3.eth.accounts[2],
                100,
            ).transact(tx_details)
            raise Exception("test_burn_caller_is_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current Timelock can call this function"
            if not "e79" in str(e):
                raise e