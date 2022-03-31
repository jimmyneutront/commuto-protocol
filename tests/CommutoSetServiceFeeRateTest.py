import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoSetServiceFeeRateTest(CommutoSwapTest.CommutoSwapTest):

    def test_setServiceFeeRate_caller_is_timelock(self):
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.commuto_swap_contract.functions.setServiceFeeRate(200).transact(tx_details)
            raise Exception("test_setServiceFeeRate_caller_is_timelock: Expected revert not received")
        except ValueError as e:
            #"e79": "Only the current Timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_setServiceFeeRate_event_emission_check(self):
        #Ensure setting the service fee rate emits an event
        ServiceFeeRateChanged_filter = self.commuto_swap_contract.events.ServiceFeeRateChanged\
            .createFilter(fromBlock="latest")
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.commuto_swap_contract.functions.setServiceFeeRate(200).transact(tx_details)
        events = ServiceFeeRateChanged_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["newServiceFeeRate"], 200)