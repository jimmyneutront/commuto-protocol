import CommutoSwapTest
from hexbytes import HexBytes
from time import sleep
from uuid import uuid4

class CommutoSwapIntegrationTests(CommutoSwapTest.CommutoSwapTest):

    def test_maker_as_seller_swap(self):
        # Testing Maker as Seller swap
        self.give_primary_timelock_CommutoSwap_control()
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address).call()
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
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        OfferOpened_event_filter = self.commuto_swap_contract.events.OfferOpened.createFilter(fromBlock="latest",
                                                                                              argument_filters={
                                                                                                  "offerID": maker_as_seller_swap_id,
                                                                                                  "interfaceId": HexBytes(
                                                                                                      "an interface Id here".encode(
                                                                                                          "utf-8").hex())})
        openOffer_tx_hash = self.commuto_swap_contract.functions.openOffer(
            maker_as_seller_swap_id,
            maker_as_seller_offer
        ).transact(tx_details)
        openOffer_tx_receipt = self.w3.eth.get_transaction_receipt(openOffer_tx_hash)
        events = OfferOpened_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["offerID"] == maker_as_seller_swap_id and events[0]["args"][
            "interfaceId"] == HexBytes("an interface Id here".encode("utf-8").hex()) and events[0][
                    "event"] == "OfferOpened"):
            raise Exception("OfferOpened event for offer with id " + str(maker_as_seller_swap_id) + " not found")
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
            "serviceFeeAmount": 100,
            "serviceFeeRate": 100,
            "direction": 1,
            "settlementMethod": "USD-SWIFT|a price here".encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100
        ).transact(tx_details)
        OfferTaken_event_filter = self.commuto_swap_contract.events.OfferTaken.createFilter(fromBlock="latest",
                                                                                            argument_filters={
                                                                                                "offerID": maker_as_seller_swap_id,
                                                                                                "takerInterfaceId": HexBytes(
                                                                                                    "an interface Id here".encode(
                                                                                                        "utf-8").hex())})
        takeOffer_tx_hash = self.commuto_swap_contract.functions.takeOffer(
            maker_as_seller_swap_id,
            maker_as_seller_swap,
        ).transact(tx_details)
        takeOffer_tx_receipt = self.w3.eth.get_transaction_receipt(takeOffer_tx_hash)
        events = OfferTaken_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["offerID"] == maker_as_seller_swap_id and events[0]["args"][
            "takerInterfaceId"] == HexBytes("an interface Id here".encode("utf-8").hex()) and events[0][
                    "event"] == "OfferTaken"):
            raise Exception("OfferTaken event for offer with id " + str(maker_as_seller_swap_id) + " not found")
        tx_details = {
            "from": self.maker_address
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            10000
        ).transact(tx_details)
        SwapFilled_event_filter = self.commuto_swap_contract.events.SwapFilled.createFilter(fromBlock="latest",
                                                                                            argument_filters={
                                                                                                "swapID": maker_as_seller_swap_id
                                                                                            })
        fundSwap_tx_hash = self.commuto_swap_contract.functions.fillSwap(
            maker_as_seller_swap_id
        ).transact(tx_details)
        fundSwap_tx_receipt = self.w3.eth.get_transaction_receipt(fundSwap_tx_hash)
        events = SwapFilled_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_seller_swap_id and events[0]["event"] ==
                "SwapFilled"):
            raise Exception("SwapFilled event for swap with id " + str(maker_as_seller_swap_id) + " not found")
        tx_details = {
            "from": self.taker_address
        }
        reportPaymentSent_tx_hash = self.commuto_swap_contract.functions.reportPaymentSent(
            maker_as_seller_swap_id
        ).transact(tx_details)
        PaymentSent_event_filter = self.commuto_swap_contract.events.PaymentSent.createFilter(fromBlock="latest",
                                                                                              argument_filters={
                                                                                                  "swapID": maker_as_seller_swap_id})
        reportPaymentSent_tx_receipt = self.w3.eth.get_transaction_receipt(reportPaymentSent_tx_hash)
        events = PaymentSent_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_seller_swap_id and events[0][
            "event"] == "PaymentSent"):
            raise Exception("PaymentSent event for swap with id " + str(maker_as_seller_swap_id) + " not found")
        tx_details = {
            "from": self.maker_address
        }
        PaymentReceived_event_filter = self.commuto_swap_contract.events.PaymentReceived.createFilter(
            fromBlock="latest",
            argument_filters={
                "swapID": maker_as_seller_swap_id})
        reportPaymentReceived_tx_hash = self.commuto_swap_contract.functions.reportPaymentReceived(
            maker_as_seller_swap_id
        ).transact(tx_details)
        reportPaymentReceieved_tx_receipt = self.w3.eth.get_transaction_receipt(reportPaymentReceived_tx_hash)
        events = PaymentReceived_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_seller_swap_id and events[0][
            "event"] == "PaymentReceived"):
            raise Exception("PaymentReceived event for swap with id " + str(maker_as_seller_swap_id) + " not found")
        SellerClosed_event_filter = self.commuto_swap_contract.events.SellerClosed.createFilter(fromBlock="latest",
                                                                                                argument_filters={
                                                                                                    "swapID": maker_as_seller_swap_id})
        maker_closeSwap_tx_hash = self.commuto_swap_contract.functions.closeSwap(
            maker_as_seller_swap_id
        ).transact(tx_details)
        maker_closeSwap_tx_receipt = self.w3.eth.get_transaction_receipt(maker_closeSwap_tx_hash)
        events = SellerClosed_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_seller_swap_id and events[0][
            "event"] == "SellerClosed"):
            raise Exception("SellerClosed event for swap with id " + str(maker_as_seller_swap_id) + " not found")
        tx_details = {
            "from": self.taker_address
        }
        taker_closeSwap_tx_hash = self.commuto_swap_contract.functions.closeSwap(
            maker_as_seller_swap_id
        ).transact(tx_details)
        BuyerClosed_event_filter = self.commuto_swap_contract.events.BuyerClosed.createFilter(fromBlock="latest",
                                                                                              argument_filters={
                                                                                                  "swapID": maker_as_seller_swap_id})
        taker_closeSwap_tx_receipt = self.w3.eth.get_transaction_receipt(taker_closeSwap_tx_hash)
        events = BuyerClosed_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_seller_swap_id and events[0][
            "event"] == "BuyerClosed"):
            raise Exception("BuyerClosed event for swap with id " + str(maker_as_seller_swap_id) + " not found")
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address)\
            .call()
        if maker_initial_dai_balance - 10100 != maker_final_dai_balance:
            raise Exception(
                "Maker did not receive valid amount for Maker as Seller swap with id " + str(maker_as_seller_swap_id))
        if taker_initial_dai_balance + 9900 != taker_final_dai_balance:
            raise Exception(
                "Taker did not receive valid amount for Maker as Seller swap with id " + str(maker_as_seller_swap_id))
        if service_fee_initial_dai_balance + 200 != service_fee_final_dai_balance:
            raise Exception("Service Fee Pool did not receive valid amount for Maker as Seller swap with id " + str(
                maker_as_seller_swap_id))

    def test_maker_as_buyer_swap(self):
        # Testing Maker as Buyer swap
        self.give_primary_timelock_CommutoSwap_control()
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address)\
            .call()
        maker_as_buyer_swap_id = HexBytes(uuid4().bytes)
        tx_details = {
            "from": self.maker_address
        }
        maker_as_buyer_offer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 100,
            "direction": 0,
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "paymentMethod": 0,
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        OfferOpened_event_filter = self.commuto_swap_contract.events.OfferOpened.createFilter(fromBlock="latest",
                                                                                              argument_filters={
                                                                                                  "offerID": maker_as_buyer_swap_id,
                                                                                                  "interfaceId": HexBytes(
                                                                                                      "an interface Id here".encode(
                                                                                                          "utf-8").hex())})
        openOffer_tx_hash = self.commuto_swap_contract.functions.openOffer(
            maker_as_buyer_swap_id,
            maker_as_buyer_offer,
        ).transact(tx_details)
        openOffer_tx_receipt = self.w3.eth.get_transaction_receipt(openOffer_tx_hash)
        events = OfferOpened_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["offerID"] == maker_as_buyer_swap_id and events[0]["args"][
            "interfaceId"] == HexBytes("an interface Id here".encode("utf-8").hex()) and events[0][
                    "event"] == "OfferOpened"):
            raise Exception("OfferOpened event for offer with id " + str(maker_as_buyer_swap_id) + " not found")
        tx_details = {
            "from": self.taker_address
        }
        maker_as_buyer_swap = {
            "isCreated": False,
            "requiresFill": False,
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
            "direction": 0,
            "settlementMethod": "USD-SWIFT|a price here".encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
            "disputeRaiser": 0,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11100
        ).transact(tx_details)
        takeOffer_tx_hash = self.commuto_swap_contract.functions.takeOffer(
            maker_as_buyer_swap_id,
            maker_as_buyer_swap,
        ).transact(tx_details)
        OfferTaken_event_filter = self.commuto_swap_contract.events.OfferTaken.createFilter(fromBlock="latest",
                                                                                            argument_filters={
                                                                                                "offerID": maker_as_buyer_swap_id,
                                                                                                "takerInterfaceId": HexBytes(
                                                                                                    "an interface Id here".encode(
                                                                                                        "utf-8").hex())})
        takeOffer_tx_receipt = self.w3.eth.get_transaction_receipt(takeOffer_tx_hash)
        tx_details = {
            "from": self.maker_address
        }
        events = OfferTaken_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["offerID"] == maker_as_buyer_swap_id and events[0]["args"][
            "takerInterfaceId"] == HexBytes("an interface Id here".encode("utf-8").hex()) and events[0][
                    "event"] == "OfferTaken"):
            raise Exception("OfferTaken event for offer with id " + str(maker_as_buyer_swap_id) + " not found")
        PaymentSent_event_filter = self.commuto_swap_contract.events.PaymentSent.createFilter(fromBlock="latest",
                                                                                              argument_filters={
                                                                                                  "swapID": maker_as_buyer_swap_id})
        reportPaymentSent_tx_hash = self.commuto_swap_contract.functions.reportPaymentSent(
            maker_as_buyer_swap_id
        ).transact(tx_details)
        reportPaymentSent_tx_receipt = self.w3.eth.get_transaction_receipt(reportPaymentSent_tx_hash)
        events = PaymentSent_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_buyer_swap_id and events[0][
            "event"] == "PaymentSent"):
            raise Exception("PaymentSent event for swap with id " + str(maker_as_buyer_swap_id) + " not found")
        tx_details = {
            "from": self.taker_address
        }
        PaymentReceived_event_filter = self.commuto_swap_contract.events.PaymentReceived.createFilter(
            fromBlock="latest",
            argument_filters={
                "swapID": maker_as_buyer_swap_id})
        reportPaymentReceived_tx_hash = self.commuto_swap_contract.functions.reportPaymentReceived(
            maker_as_buyer_swap_id
        ).transact(tx_details)
        reportPaymentReceieved_tx_receipt = self.w3.eth.get_transaction_receipt(reportPaymentReceived_tx_hash)
        events = PaymentReceived_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_buyer_swap_id and events[0][
            "event"] == "PaymentReceived"):
            raise Exception("PaymentReceived event for swap with id " + str(maker_as_buyer_swap_id) + " not found")
        SellerClosed_event_filter = self.commuto_swap_contract.events.SellerClosed.createFilter(fromBlock="latest",
                                                                                                argument_filters={
                                                                                                    "swapID": maker_as_buyer_swap_id})
        taker_closeSwap_tx_hash = self.commuto_swap_contract.functions.closeSwap(
            maker_as_buyer_swap_id
        ).transact(tx_details)
        taker_closeSwap_tx_receipt = self.w3.eth.get_transaction_receipt(taker_closeSwap_tx_hash)
        events = SellerClosed_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_buyer_swap_id and events[0][
            "event"] == "SellerClosed"):
            raise Exception("SellerClosed event for swap with id " + str(maker_as_buyer_swap_id) + " not found")
        tx_details = {
            "from": self.maker_address
        }
        BuyerClosed_event_filter = self.commuto_swap_contract.events.BuyerClosed.createFilter(fromBlock="latest",
                                                                                              argument_filters={
                                                                                                  "swapID": maker_as_buyer_swap_id})
        maker_closeSwap_tx_hash = self.commuto_swap_contract.functions.closeSwap(
            maker_as_buyer_swap_id
        ).transact(tx_details)
        maker_closeSwap_tx_receipt = self.w3.eth.get_transaction_receipt(maker_closeSwap_tx_hash)
        events = BuyerClosed_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_buyer_swap_id and events[0][
            "event"] == "BuyerClosed"):
            raise Exception("BuyerClosed event for swap with id " + str(maker_as_buyer_swap_id) + " not found")
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address)\
            .call()
        if maker_initial_dai_balance + 9900 != maker_final_dai_balance:
            raise Exception(
                "Maker did not receive valid amount for Maker as Buyer swap with id " + str(maker_as_buyer_swap_id))
        if taker_initial_dai_balance - 10100 != taker_final_dai_balance:
            raise Exception(
                "Taker did not receive valid amount for Maker as Buyer swap with id " + str(maker_as_buyer_swap_id))
        if service_fee_initial_dai_balance + 200 != service_fee_final_dai_balance:
            raise Exception("Service Fee Pool did not receive valid amount for Maker as Buyer swap with id " + str(
                maker_as_buyer_swap_id))

    def test_disputed_swap_with_agreement(self):
        #Test disputed swap payout given agreement by maker and taker
        self.give_primary_timelock_CommutoSwap_control()
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        disputed_swap_with_agreement_id = HexBytes(uuid4().bytes)
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
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            disputed_swap_with_agreement_id,
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
            "settlementMethod": "USD-SWIFT|a price here".encode("utf-8"),
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
            disputed_swap_with_agreement_id,
            newSwap,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.raiseDispute(
            disputed_swap_with_agreement_id,
            self.dispute_agent_0,
            self.dispute_agent_1,
            self.dispute_agent_2
        ).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_0
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_agreement_id, 1000, 500, 500).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_agreement_id, 1000, 500, 500).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_2
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_agreement_id, 1000, 500, 500).transact(tx_details)
        tx_details = {
            "from": self.maker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(disputed_swap_with_agreement_id, 1).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(disputed_swap_with_agreement_id, 1).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.closeDisputedSwap(disputed_swap_with_agreement_id).transact(tx_details)
        tx_details = {
            "from": self.maker_address
        }
        self.commuto_swap_contract.functions.closeDisputedSwap(disputed_swap_with_agreement_id).transact(tx_details)
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        escalatedDisputedSwapsPool_final_balance = self.test_dai_contract.functions.balanceOf(
            self.w3.eth.accounts[6]).call()
        self.assertEqual(maker_initial_dai_balance - 100, maker_final_dai_balance)
        self.assertEqual(taker_initial_dai_balance - 600, taker_final_dai_balance)
        self.assertEqual(service_fee_initial_dai_balance + 700, service_fee_final_dai_balance)

    def test_immediate_escalation_given_rejection(self):
        #Test immediate escalation to token holders given rejection of resolution proposal
        self.give_primary_timelock_CommutoSwap_control()
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        disputed_swap_with_rejection_id = HexBytes(uuid4().bytes)
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
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            disputed_swap_with_rejection_id,
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
            "settlementMethod": "USD-SWIFT|a price here".encode("utf-8"),
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
            disputed_swap_with_rejection_id,
            newSwap,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.raiseDispute(
            disputed_swap_with_rejection_id,
            self.dispute_agent_0,
            self.dispute_agent_1,
            self.dispute_agent_2
        ).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_0
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_rejection_id, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_rejection_id, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.dispute_agent_2
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_rejection_id, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.maker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(disputed_swap_with_rejection_id, 2).transact(
            tx_details)
        tx_details = {
            "from": self.w3.eth.accounts[2]
        }
        self.commuto_swap_contract.functions.closeEscalatedSwap(disputed_swap_with_rejection_id,
                                                                500, 0, 1500
                                                                ).transact(tx_details)
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        self.assertEqual(maker_initial_dai_balance - 600, maker_final_dai_balance)
        self.assertEqual(taker_initial_dai_balance - 1100, taker_final_dai_balance)
        self.assertEqual(service_fee_initial_dai_balance + 1700, service_fee_final_dai_balance)

    def test_escalation_given_no_response(self):
        #Test escalation to token holders given no response from dispute agents
        self.give_primary_timelock_CommutoSwap_control()
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        disputed_swap_with_no_response_id = HexBytes(uuid4().bytes)
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
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            disputed_swap_with_no_response_id,
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
            "settlementMethod": "USD-SWIFT|a price here".encode("utf-8"),
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
            disputed_swap_with_no_response_id,
            newSwap,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.raiseDispute(
            disputed_swap_with_no_response_id,
            self.dispute_agent_0,
            self.dispute_agent_1,
            self.dispute_agent_2
        ).transact(tx_details)
        self.mine_blocks(5)
        self.commuto_swap_contract.functions.escalateDispute(disputed_swap_with_no_response_id, 1).transact(tx_details)
        tx_details = {
            "from": self.w3.eth.accounts[2]
        }
        self.commuto_swap_contract.functions.closeEscalatedSwap(disputed_swap_with_no_response_id,
                                                                500, 0, 1500
                                                                ).transact(tx_details)
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        self.assertEqual(maker_initial_dai_balance - 600, maker_final_dai_balance)
        self.assertEqual(taker_initial_dai_balance - 1100, taker_final_dai_balance)
        self.assertEqual(service_fee_initial_dai_balance + 1700, service_fee_final_dai_balance)

    def test_escalation_no_maker_response(self):
        #Test escalation to token holders given lack of response from maker
        self.give_primary_timelock_CommutoSwap_control()
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        disputed_swap_no_maker_response = HexBytes(uuid4().bytes)
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
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            disputed_swap_no_maker_response,
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
            "settlementMethod": "USD-SWIFT|a price here".encode("utf-8"),
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
            disputed_swap_no_maker_response,
            newSwap,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.raiseDispute(
            disputed_swap_no_maker_response,
            self.dispute_agent_0,
            self.dispute_agent_1,
            self.dispute_agent_2
        ).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_0
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_no_maker_response, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_no_maker_response, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.dispute_agent_2
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_no_maker_response, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(disputed_swap_no_maker_response, 1).transact(
            tx_details)
        self.mine_blocks(1)
        self.commuto_swap_contract.functions.escalateDispute(disputed_swap_no_maker_response, 2).transact(tx_details)
        tx_details = {
            "from": self.w3.eth.accounts[2]
        }
        self.commuto_swap_contract.functions.closeEscalatedSwap(disputed_swap_no_maker_response,
                                                                500, 0, 1500
                                                                ).transact(tx_details)
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        self.assertEqual(maker_initial_dai_balance - 600, maker_final_dai_balance)
        self.assertEqual(taker_initial_dai_balance - 1100, taker_final_dai_balance)
        self.assertEqual(service_fee_initial_dai_balance + 1700, service_fee_final_dai_balance)

    def test_escalation_no_taker_response(self):
        #Test escalation to token holders given lack of response from taker
        self.give_primary_timelock_CommutoSwap_control()
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        disputed_swap_no_taker_response = HexBytes(uuid4().bytes)
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
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            disputed_swap_no_taker_response,
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
            "settlementMethod": "USD-SWIFT|a price here".encode("utf-8"),
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
            disputed_swap_no_taker_response,
            newSwap,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.raiseDispute(
            disputed_swap_no_taker_response,
            self.dispute_agent_0,
            self.dispute_agent_1,
            self.dispute_agent_2
        ).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_0
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_no_taker_response, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_no_taker_response, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.dispute_agent_2
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_no_taker_response, 1000, 500, 500).transact(
            tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(disputed_swap_no_taker_response, 1).transact(
            tx_details)
        self.mine_blocks(1)
        self.commuto_swap_contract.functions.escalateDispute(disputed_swap_no_taker_response, 2).transact(tx_details)
        tx_details = {
            "from": self.w3.eth.accounts[2]
        }
        self.commuto_swap_contract.functions.closeEscalatedSwap(disputed_swap_no_taker_response,
                                                                500, 0, 1500
                                                                ).transact(tx_details)
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.primary_timelock_contract.address) \
            .call()
        self.assertEqual(maker_initial_dai_balance - 600, maker_final_dai_balance)
        self.assertEqual(taker_initial_dai_balance - 1100, taker_final_dai_balance)
        self.assertEqual(service_fee_initial_dai_balance + 1700, service_fee_final_dai_balance)