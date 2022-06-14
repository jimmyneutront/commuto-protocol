import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4


class CommutoCancelOfferTest(CommutoSwapTest.CommutoSwapTest):

    def test_cancelOffer_existence_check(self):
        # Ensure cancelOffer checks for offer existence
        try:
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.cancelOffer(
                HexBytes(uuid4().bytes)
            ).transact(tx_details)
            raise (Exception("test_cancelOffer_existence_check failed without raising exception"))
        except ValueError as e:
            # "e15":"An offer with the specified id does not exist"
            if "e15" not in str(e):
                raise e

    def test_cancelOffer_caller_is_maker_check(self):
        # Ensure cancelOffer checks that caller is maker
        try:
            new_offer_id = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address,
            }
            new_offer = {
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
                new_offer_id,
                new_offer,
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.cancelOffer(
                new_offer_id,
            ).transact(tx_details)
            raise (Exception("test_cancelOffer_caller_is_maker_check failed without raising exception"))
        except ValueError as e:
            # "e17":"Offers can only be mutated by offer maker"
            if "e17" not in str(e):
                raise e

    def test_cancelOffer_taken_offer_check(self):
        # Ensure that taken offers cannot be canceled
        try:
            new_offer_id = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address,
            }
            new_offer = {
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
                new_offer_id,
                new_offer,
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            new_swap = {
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
                new_offer_id,
                new_swap,
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.cancelOffer(
                new_offer_id
            ).transact(tx_details)
            raise (Exception("test_cancelOffer_taken_offer_check failed without raising exception"))
        except ValueError as e:
            # "e16":"Offer is taken and cannot be mutated"
            if "e16" not in str(e):
                raise e

    def test_cancelOffer_cancels_offer(self):
        # Ensure cancelOffer actually cancels the offer
        maker_initial_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        maker_as_seller_offer_id = HexBytes(uuid4().bytes)
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
            "price": HexBytes("a price here".encode("utf-8").hex()),
            "settlementMethods": ["USD-SWIFT".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1100,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            maker_as_seller_offer_id,
            maker_as_seller_offer
        ).transact(tx_details)
        # we supress the inspection here because "OfferCanceled" is the actual name of the event
        # noinspection PyPep8Naming
        OfferCanceled_event_filter = self.commuto_swap_contract.events.OfferCanceled.createFilter(
            fromBlock="latest",
            argument_filters={
                "offerID": maker_as_seller_offer_id
            }
        )
        self.commuto_swap_contract.functions.cancelOffer(
            maker_as_seller_offer_id
        ).transact(tx_details)
        maker_final_dai_balance = self.test_dai_contract.functions.balanceOf(self.maker_address).call()
        assert(maker_final_dai_balance == maker_initial_dai_balance)
        events = OfferCanceled_event_filter.get_new_entries()
        if not (len(events) == 1 and events[0]["args"]["offerID"] == maker_as_seller_offer_id and events[0]["event"] ==
                "OfferCanceled"):
            raise Exception("OfferCanceled event for offer with id " + str(maker_as_seller_offer_id) + " was not found")
