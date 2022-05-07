import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoSetMinimumDisputePeriodTest(CommutoSwapTest.CommutoSwapTest):

    def test_setMinimumDisputePeriod_caller_is_primary_timelock(self):
        #Ensure that the caller of the setMinimumDisputePeriod function is the primary timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.commuto_swap_contract.functions.setMinimumDisputePeriod(10).transact(tx_details)
            raise Exception("test_setMinimumDisputePeriod_caller_is_primary_timelock: Expected revert not received")
        except ValueError as e:
            #"e79": "Only the current primary timelock can call this function"
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

    def test_setMinimumDisputePeriod_success(self):
        #Ensure that the minimum dispute period is actually changed
        newOfferID = HexBytes(uuid4().bytes)
        tx_details = {
            "from": self.maker_address
        }
        newOffer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 1,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            newOfferID,
            newOffer,
        ).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        newSwap = {
            "isCreated": False,
            "requiresFill": True,
            "maker": self.maker_address,
            "makerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
            "taker": self.taker_address,
            "takerInterfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "takenSwapAmount": 10000,
            "serviceFeeAmount": 100,
            "serviceFeeRate": 100,
            "direction": 1,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethod": "USD-SWIFT".encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.takeOffer(
            newOfferID,
            newSwap,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.raiseDispute(
            newOfferID,
            self.dispute_agent_0,
            self.dispute_agent_1,
            self.dispute_agent_2
        ).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_0
        }
        self.commuto_swap_contract.functions.proposeResolution(newOfferID, 1000, 1000, 0).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(newOfferID, 1000, 1000, 0).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        try:
            self.commuto_swap_contract.functions.escalateDispute(newOfferID, 2).transact(tx_details)
            raise Exception("test_setMinimumDisputePeriod_success: Expected revert not received")
        except ValueError as e:
            # "e71": "More blocks must be mined before swap can be escalated"
            if not "e71" in str(e):
                raise e
        self.mine_blocks(7)
        DisputeEscalated_event_filter = self.commuto_swap_contract.events.DisputeEscalated \
            .createFilter(fromBlock="latest",
                          argument_filters={
                              'swapID': newOfferID
                          }
                          )
        self.commuto_swap_contract.functions.escalateDispute(newOfferID, 2).transact(tx_details)
        events = DisputeEscalated_event_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["swapID"], newOfferID)
        self.assertEqual(events[0]["args"]["escalator"], self.taker_address)
        self.assertEqual(events[0]["args"]["reason"], 2)