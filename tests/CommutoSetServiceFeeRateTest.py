import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoSetServiceFeeRateTest(CommutoSwapTest.CommutoSwapTest):

    def test_setServiceFeeRate_caller_is_timelock(self):
        #Ensure the caller of the setServiceFeeRate function is the timelock
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

    def test_setServiceFeeRate_success(self):
        #Ensure that the service fee rate is actually changed
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        initial_service_fee_rate = self.commuto_swap_contract.functions.getServiceFeeRate().call()
        self.assertEqual(initial_service_fee_rate, 100)
        self.commuto_swap_contract.functions.setServiceFeeRate(200).transact(tx_details)
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(
            self.w3.eth.accounts[2]).call()
        maker_as_seller_swap_id = HexBytes(uuid4().bytes)
        tx_details = {
            "from": self.maker_address,
        }
        maker_as_seller_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 200,
            "direction": 1,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1200,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            maker_as_seller_swap_id,
            maker_as_seller_offer
        ).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        maker_as_seller_swap = {
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
            "serviceFeeAmount": 200,
            "serviceFeeRate": 200,
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
            1200
        ).transact(tx_details)
        self.commuto_swap_contract.functions.takeOffer(
            maker_as_seller_swap_id,
            maker_as_seller_swap,
        ).transact(tx_details)
        tx_details = {
            "from": self.maker_address
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            10000
        ).transact(tx_details)
        self.commuto_swap_contract.functions.fillSwap(
            maker_as_seller_swap_id
        ).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.reportPaymentSent(
            maker_as_seller_swap_id
        ).transact(tx_details)
        tx_details = {
            "from": self.maker_address
        }
        self.commuto_swap_contract.functions.reportPaymentReceived(maker_as_seller_swap_id).transact(tx_details)
        self.commuto_swap_contract.functions.closeSwap(maker_as_seller_swap_id).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.closeSwap(maker_as_seller_swap_id).transact(tx_details)
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.w3.eth.accounts[2]).call()
        self.assertEqual(maker_final_dai_balance + 10200, maker_initial_dai_balance)
        self.assertEqual(taker_final_dai_balance - 9800, taker_initial_dai_balance)
        self.assertEqual(service_fee_final_dai_balance - 400, service_fee_initial_dai_balance)