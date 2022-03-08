import CommutoSwapTest

class CommutoDisputeAgentTest(CommutoSwapTest.CommutoSwapTest):

    def test_dispute_agent_active_setter_is_owner_check(self):
        #Ensure the caller of setDisputeAgentActive is the CommutoSwap contract owner
        try:
            tx_details = {
                "from": self.maker_address
            }
            tx_hash = self.commuto_swap_contract.functions.setDisputeAgentActive(self.maker_address, True).transact(tx_details)
            raise (Exception("test_dispute_agent_active_setter_is_owner_check failed without raising exception"))
        except ValueError as e:
            # "e1": "Only contract owner can set dispute agent activity state"
            if not "e1" in str(e):
                raise e