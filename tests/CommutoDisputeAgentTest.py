import CommutoSwapTest

class CommutoDisputeAgentTest(CommutoSwapTest.CommutoSwapTest):

    def test_dispute_agent_active_setter_is_owner_check(self):
        #Ensure the address of the caller of setDisputeAgentActive equals that of the primary timelock
        try:
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.setDisputeAgentActive(self.maker_address, True).transact(tx_details)
            raise (Exception("test_dispute_agent_active_setter_is_owner_check failed without raising exception"))
        except ValueError as e:
            # "e1": "Only the current primary timelock can set dispute agent activity state"
            if not "e1" in str(e):
                raise e

    def test_dispute_agent_address_added_check(self):
        #Ensure that a dispute agent's address is actually set as active
        active_dispute_agents = self.commuto_swap_contract.functions.getActiveDisputeAgents().call()
        self.assertEqual(len(active_dispute_agents), 3, "unexpected number of dispute agents found")
        self.assertEqual(active_dispute_agents[0], self.dispute_agent_0, "dispute_agent_0 address not found")
        self.assertEqual(active_dispute_agents[1], self.dispute_agent_1, "dispute_agent_1 address not found")
        self.assertEqual(active_dispute_agents[2], self.dispute_agent_2, "dispute_agent_2 address not found")

    def test_dispute_agent_address_removed_check(self):
        #Ensure that a dispute agent's address is actually set as not active
        tx_details = {
            "from": self.commuto_service_fee_account
        }
        self.commuto_swap_contract.functions.setDisputeAgentActive(self.w3.eth.accounts[6], True).transact(tx_details)
        active_dispute_agents = self.commuto_swap_contract.functions.getActiveDisputeAgents().call()
        self.assertEqual(len(active_dispute_agents), 4)
        self.assertEqual(active_dispute_agents[3], self.w3.eth.accounts[6], "self.w3.eth.accounts[6] address not found")
        self.commuto_swap_contract.functions.setDisputeAgentActive(self.w3.eth.accounts[6], False).transact(tx_details)
        active_dispute_agents = self.commuto_swap_contract.functions.getActiveDisputeAgents().call()
        self.assertEqual(len(active_dispute_agents), 3, "unexpected number of dispute agents found")
        self.assertEqual(active_dispute_agents[0], self.dispute_agent_0, "dispute_agent_0 address not found")
        self.assertEqual(active_dispute_agents[1], self.dispute_agent_1, "dispute_agent_1 address not found")
        self.assertEqual(active_dispute_agents[2], self.dispute_agent_2, "dispute_agent_2 address not found")