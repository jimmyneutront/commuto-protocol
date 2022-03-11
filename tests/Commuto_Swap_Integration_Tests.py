import CommutoSwapTest
from hexbytes import HexBytes
from time import sleep
from uuid import uuid4

# TODO: Test escalation to token holders given no response from dispute agents

# TODO: Test escalation to token holders given lack of response from maker
# TODO: Test escalation to token holders given lack of response from taker

# TODO: Check payout amounts for each test

class CommutoSwapIntegrationTests(CommutoSwapTest.CommutoSwapTest):

    def test_maker_as_seller_swap(self):
        # Testing Maker as Seller swap
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.commuto_service_fee_account).call()
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
            "amountLowerBound": 100,
            "amountUpperBound": 100,
            "securityDepositAmount": 10,
            "direction": 1,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11,
        ).transact(tx_details)
        openOffer_tx_hash = self.commuto_swap_contract.functions.openOffer(
            maker_as_seller_swap_id,
            maker_as_seller_offer
        ).transact(tx_details)
        openOffer_tx_receipt = self.w3.eth.get_transaction_receipt(openOffer_tx_hash)
        OfferOpened_event_filter = self.commuto_swap_contract.events.OfferOpened.createFilter(fromBlock="latest",
                                                                                         argument_filters={
                                                                                             "offerID": maker_as_seller_swap_id,
                                                                                             "interfaceId": HexBytes(
                                                                                                 "an interface Id here".encode(
                                                                                                     "utf-8").hex())})
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
            "amountLowerBound": 100,
            "amountUpperBound": 100,
            "securityDepositAmount": 10,
            "takenSwapAmount": 100,
            "serviceFeeAmount": 1,
            "direction": 1,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethod": "USD-SWIFT".encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11
        ).transact(tx_details)
        takeOffer_tx_hash = self.commuto_swap_contract.functions.takeOffer(
            maker_as_seller_swap_id,
            maker_as_seller_swap,
        ).transact(tx_details)
        takeOffer_tx_receipt = self.w3.eth.get_transaction_receipt(takeOffer_tx_hash)
        OfferTaken_event_filter = self.commuto_swap_contract.events.OfferTaken.createFilter(fromBlock="latest",
                                                                                       argument_filters={
                                                                                           "offerID": maker_as_seller_swap_id,
                                                                                           "takerInterfaceId": HexBytes(
                                                                                               "an interface Id here".encode(
                                                                                                   "utf-8").hex())})
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
            100
        ).transact(tx_details)
        fundSwap_tx_hash = self.commuto_swap_contract.functions.fillSwap(
            maker_as_seller_swap_id
        ).transact(tx_details)
        fundSwap_tx_receipt = self.w3.eth.get_transaction_receipt(fundSwap_tx_hash)
        SwapFilled_event_filter = self.commuto_swap_contract.events.SwapFilled.createFilter(fromBlock="latest",
                                                                                       argument_filters={
                                                                                           "swapID": maker_as_seller_swap_id
                                                                                       })
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
        reportPaymentSent_tx_receipt = self.w3.eth.get_transaction_receipt(reportPaymentSent_tx_hash)
        PaymentSent_event_filter = self.commuto_swap_contract.events.PaymentSent.createFilter(fromBlock="latest",
                                                                                         argument_filters={
                                                                                             "swapID": maker_as_seller_swap_id})
        events = PaymentSent_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_seller_swap_id and events[0][
            "event"] == "PaymentSent"):
            raise Exception("PaymentSent event for swap with id " + str(maker_as_seller_swap_id) + " not found")
        tx_details = {
            "from": self.maker_address
        }
        reportPaymentReceived_tx_hash = self.commuto_swap_contract.functions.reportPaymentReceived(
            maker_as_seller_swap_id
        ).transact(tx_details)
        reportPaymentReceieved_tx_receipt = self.w3.eth.get_transaction_receipt(reportPaymentReceived_tx_hash)
        PaymentReceived_event_filter = self.commuto_swap_contract.events.PaymentReceived.createFilter(fromBlock="latest",
                                                                                                 argument_filters={
                                                                                                     "swapID": maker_as_seller_swap_id})
        events = PaymentReceived_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_seller_swap_id and events[0][
            "event"] == "PaymentReceived"):
            raise Exception("PaymentReceived event for swap with id " + str(maker_as_seller_swap_id) + " not found")
        maker_closeSwap_tx_hash = self.commuto_swap_contract.functions.closeSwap(
            maker_as_seller_swap_id
        ).transact(tx_details)
        maker_closeSwap_tx_receipt = self.w3.eth.get_transaction_receipt(maker_closeSwap_tx_hash)
        SellerClosed_event_filter = self.commuto_swap_contract.events.SellerClosed.createFilter(fromBlock="latest",
                                                                                           argument_filters={
                                                                                               "swapID": maker_as_seller_swap_id})
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
        taker_closeSwap_tx_receipt = self.w3.eth.get_transaction_receipt(taker_closeSwap_tx_hash)
        BuyerClosed_event_filter = self.commuto_swap_contract.events.BuyerClosed.createFilter(fromBlock="latest",
                                                                                         argument_filters={
                                                                                             "swapID": maker_as_seller_swap_id})
        events = BuyerClosed_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_seller_swap_id and events[0][
            "event"] == "BuyerClosed"):
            raise Exception("BuyerClosed event for swap with id " + str(maker_as_seller_swap_id) + " not found")
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.commuto_service_fee_account)\
            .call()
        if maker_initial_dai_balance - 101 != maker_final_dai_balance:
            raise Exception(
                "Maker did not receive valid amount for Maker as Seller swap with id " + str(maker_as_seller_swap_id))
        if taker_initial_dai_balance + 99 != taker_final_dai_balance:
            raise Exception(
                "Taker did not receive valid amount for Maker as Seller swap with id " + str(maker_as_seller_swap_id))
        if service_fee_initial_dai_balance + 2 != service_fee_final_dai_balance:
            raise Exception("Service Fee Pool did not receive valid amount for Maker as Seller swap with id " + str(
                maker_as_seller_swap_id))

    def test_maker_as_buyer_swap(self):
        # Testing Maker as Buyer swap
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.commuto_service_fee_account)\
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
            "amountLowerBound": 100,
            "amountUpperBound": 100,
            "securityDepositAmount": 10,
            "direction": 0,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
            "paymentMethod": 0,
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11,
        ).transact(tx_details)
        openOffer_tx_hash = self.commuto_swap_contract.functions.openOffer(
            maker_as_buyer_swap_id,
            maker_as_buyer_offer,
        ).transact(tx_details)
        openOffer_tx_receipt = self.w3.eth.get_transaction_receipt(openOffer_tx_hash)
        OfferOpened_event_filter = self.commuto_swap_contract.events.OfferOpened.createFilter(fromBlock="latest",
                                                                                         argument_filters={
                                                                                             "offerID": maker_as_buyer_swap_id,
                                                                                             "interfaceId": HexBytes(
                                                                                                 "an interface Id here".encode(
                                                                                                     "utf-8").hex())})
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
            "amountLowerBound": 100,
            "amountUpperBound": 100,
            "securityDepositAmount": 10,
            "takenSwapAmount": 100,
            "serviceFeeAmount": 1,
            "direction": 0,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethod": "USD-SWIFT".encode("utf-8"),
            "protocolVersion": 1,
            "isPaymentSent": True,
            "isPaymentReceived": True,
            "hasBuyerClosed": True,
            "hasSellerClosed": True,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            111
        ).transact(tx_details)
        takeOffer_tx_hash = self.commuto_swap_contract.functions.takeOffer(
            maker_as_buyer_swap_id,
            maker_as_buyer_swap,
        ).transact(tx_details)
        takeOffer_tx_receipt = self.w3.eth.get_transaction_receipt(takeOffer_tx_hash)
        tx_details = {
            "from": self.maker_address
        }
        OfferTaken_event_filter = self.commuto_swap_contract.events.OfferTaken.createFilter(fromBlock="latest",
                                                                                       argument_filters={
                                                                                           "offerID": maker_as_buyer_swap_id,
                                                                                           "takerInterfaceId": HexBytes(
                                                                                               "an interface Id here".encode(
                                                                                                   "utf-8").hex())})
        events = OfferTaken_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["offerID"] == maker_as_buyer_swap_id and events[0]["args"][
            "takerInterfaceId"] == HexBytes("an interface Id here".encode("utf-8").hex()) and events[0][
                    "event"] == "OfferTaken"):
            raise Exception("OfferTaken event for offer with id " + str(maker_as_buyer_swap_id) + " not found")
        reportPaymentSent_tx_hash = self.commuto_swap_contract.functions.reportPaymentSent(
            maker_as_buyer_swap_id
        ).transact(tx_details)
        reportPaymentSent_tx_receipt = self.w3.eth.get_transaction_receipt(reportPaymentSent_tx_hash)
        PaymentSent_event_filter = self.commuto_swap_contract.events.PaymentSent.createFilter(fromBlock="latest",
                                                                                         argument_filters={
                                                                                             "swapID": maker_as_buyer_swap_id})
        events = PaymentSent_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_buyer_swap_id and events[0][
            "event"] == "PaymentSent"):
            raise Exception("PaymentSent event for swap with id " + str(maker_as_buyer_swap_id) + " not found")
        tx_details = {
            "from": self.taker_address
        }
        reportPaymentReceived_tx_hash = self.commuto_swap_contract.functions.reportPaymentReceived(
            maker_as_buyer_swap_id
        ).transact(tx_details)
        reportPaymentReceieved_tx_receipt = self.w3.eth.get_transaction_receipt(reportPaymentReceived_tx_hash)
        PaymentReceived_event_filter = self.commuto_swap_contract.events.PaymentReceived.createFilter(fromBlock="latest",
                                                                                                 argument_filters={
                                                                                                     "swapID": maker_as_buyer_swap_id})
        events = PaymentReceived_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_buyer_swap_id and events[0][
            "event"] == "PaymentReceived"):
            raise Exception("PaymentReceived event for swap with id " + str(maker_as_buyer_swap_id) + " not found")
        taker_closeSwap_tx_hash = self.commuto_swap_contract.functions.closeSwap(
            maker_as_buyer_swap_id
        ).transact(tx_details)
        taker_closeSwap_tx_receipt = self.w3.eth.get_transaction_receipt(taker_closeSwap_tx_hash)
        SellerClosed_event_filter = self.commuto_swap_contract.events.SellerClosed.createFilter(fromBlock="latest",
                                                                                           argument_filters={
                                                                                               "swapID": maker_as_buyer_swap_id})
        events = SellerClosed_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_buyer_swap_id and events[0][
            "event"] == "SellerClosed"):
            raise Exception("SellerClosed event for swap with id " + str(maker_as_buyer_swap_id) + " not found")
        tx_details = {
            "from": self.maker_address
        }
        maker_closeSwap_tx_hash = self.commuto_swap_contract.functions.closeSwap(
            maker_as_buyer_swap_id
        ).transact(tx_details)
        maker_closeSwap_tx_receipt = self.w3.eth.get_transaction_receipt(maker_closeSwap_tx_hash)
        BuyerClosed_event_filter = self.commuto_swap_contract.events.BuyerClosed.createFilter(fromBlock="latest",
                                                                                         argument_filters={
                                                                                             "swapID": maker_as_buyer_swap_id})
        events = BuyerClosed_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["swapID"] == maker_as_buyer_swap_id and events[0][
            "event"] == "BuyerClosed"):
            raise Exception("BuyerClosed event for swap with id " + str(maker_as_buyer_swap_id) + " not found")
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.commuto_service_fee_account)\
            .call()
        if maker_initial_dai_balance + 99 != maker_final_dai_balance:
            raise Exception(
                "Maker did not receive valid amount for Maker as Buyer swap with id " + str(maker_as_buyer_swap_id))
        if taker_initial_dai_balance - 101 != taker_final_dai_balance:
            raise Exception(
                "Taker did not receive valid amount for Maker as Buyer swap with id " + str(maker_as_buyer_swap_id))
        if service_fee_initial_dai_balance + 2 != service_fee_final_dai_balance:
            raise Exception("Service Fee Pool did not receive valid amount for Maker as Buyer swap with id " + str(
                maker_as_buyer_swap_id))

    def test_disputed_swap_with_agreement(self):
        #Test disputed swap payout given agreement by maker and taker
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.commuto_service_fee_account) \
            .call()
        escalatedDisputedSwapsPool_initial_balance = self.test_dai_contract.functions.balanceOf(self.w3.eth.accounts[6]).call()
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
            "amountLowerBound": 100,
            "amountUpperBound": 100,
            "securityDepositAmount": 10,
            "direction": 1,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11,
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
            "amountLowerBound": 100,
            "amountUpperBound": 100,
            "securityDepositAmount": 10,
            "takenSwapAmount": 100,
            "serviceFeeAmount": 1,
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
            11,
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
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_agreement_id, 10, 5, 5).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_agreement_id, 10, 5, 5).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_2
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_agreement_id, 10, 5, 5).transact(tx_details)
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
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.commuto_service_fee_account) \
            .call()
        escalatedDisputedSwapsPool_final_balance = self.test_dai_contract.functions.balanceOf(
            self.w3.eth.accounts[6]).call()
        self.assertEqual(maker_initial_dai_balance - 1, maker_final_dai_balance)
        self.assertEqual(taker_initial_dai_balance - 6, taker_final_dai_balance)
        self.assertEqual(service_fee_initial_dai_balance + 7, service_fee_final_dai_balance)
        self.assertEqual(escalatedDisputedSwapsPool_initial_balance, escalatedDisputedSwapsPool_final_balance)

    def test_immediate_escalation_given_rejection(self):
        #Test immediate escalation to token holders given rejection of resolution proposal
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.commuto_service_fee_account) \
            .call()
        escalatedDisputedSwapsPool_initial_balance = self.test_dai_contract.functions.balanceOf(
            self.w3.eth.accounts[6]).call()
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
            "amountLowerBound": 100,
            "amountUpperBound": 100,
            "securityDepositAmount": 10,
            "direction": 1,
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            11,
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
            "amountLowerBound": 100,
            "amountUpperBound": 100,
            "securityDepositAmount": 10,
            "takenSwapAmount": 100,
            "serviceFeeAmount": 1,
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
            11,
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
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_rejection_id, 10, 5, 5).transact(
            tx_details)
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_rejection_id, 10, 5, 5).transact(
            tx_details)
        tx_details = {
            "from": self.dispute_agent_2
        }
        self.commuto_swap_contract.functions.proposeResolution(disputed_swap_with_rejection_id, 10, 5, 5).transact(
            tx_details)
        tx_details = {
            "from": self.maker_address
        }
        sleep(3)
        self.commuto_swap_contract.functions.reactToResolutionProposal(disputed_swap_with_rejection_id, 2).transact(
            tx_details)
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        taker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.taker_address).call()
        service_fee_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.commuto_service_fee_account) \
            .call()
        escalatedDisputedSwapsPool_final_balance = self.test_dai_contract.functions.balanceOf(
            self.w3.eth.accounts[6]).call()
        self.assertEqual(maker_initial_dai_balance - 11, maker_final_dai_balance)
        self.assertEqual(taker_initial_dai_balance - 11, taker_final_dai_balance)
        self.assertEqual(service_fee_initial_dai_balance + 2, service_fee_final_dai_balance)
        self.assertEqual(escalatedDisputedSwapsPool_initial_balance + 20, escalatedDisputedSwapsPool_final_balance)