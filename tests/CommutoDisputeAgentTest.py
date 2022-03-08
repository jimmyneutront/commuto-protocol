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

    def test_dispute_agent_address_added_check(self):
        #Ensure that a dispute agent's address is actually set as active
        active_dispute_agents = self.commuto_swap_contract.functions.getActiveDisputeAgents().call()
        self.assertEqual(len(active_dispute_agents), 3)
        self.assertEqual(active_dispute_agents[0], self.dispute_agent_0, "dispute_agent_0 address not found")
        self.assertEqual(active_dispute_agents[1], self.dispute_agent_1, "dispute_agent_1 address not found")
        self.assertEqual(active_dispute_agents[2], self.dispute_agent_2, "dispute_agent_2 address not found")

    #TODO: check that dispute agent is actually removed