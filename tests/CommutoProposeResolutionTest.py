import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoProposeResolutionTest(CommutoSwapTest.CommutoSwapTest):

    def test_proposeResolution_swap_is_disputed_check(self):
        #Ensure that a resolution can't be proposed for a swap that isn't disputed or doesn't exist
        try:
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.proposeResolution(uuid4().bytes, 0, 0, 0).transact(tx_details)
            raise (Exception("test_proposeResolution_swap_is_disputed_check failed without raising exception"))
        except ValueError as e:
            # "e54": "Swap doesn't exist or isn't disputed"
            if not "e54" in str(e):
                raise e

    def test_proposeResolution_total_payout_equals_total_unspent_locked(self):
        #Ensure total payout amount in resolution proposals must equal total amount locked in escrow, minus spent service fees
        try:
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 10, 0).transact(tx_details)
        except ValueError as e:
            # "e56": "Total payout amount must equal total amount paid in minus service fees"
            if not "e56" in str(e):
                raise e

    def test_proposeResolution_caller_is_assigned_dispute_agent_check(self):
        #Ensure resolution proposals for a swap can only be submitted by dispute agents selected for the swap
        try:
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
                newOfferID,
                newSwap,
            ).transact(tx_details)
            self.commuto_swap_contract.functions.raiseDispute(
                newOfferID,
                self.dispute_agent_0,
                self.dispute_agent_1,
                self.dispute_agent_2
            ).transact(tx_details)
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            raise (Exception("test_proposeResolution_caller_is_assigned_dispute_agent_check failed without raising exception"))
        except ValueError as e:
            # "e55": "Only a dispute agent selected for the swap can propose a resolution"
            if not "e55" in str(e):
                raise e

    def test_proposeResolution_emits_event(self):
        #Ensure proposeResolution emits ResolutionProposed event upon success
        newOfferID = HexBytes(uuid4().bytes)
        ResolutionProposed_event_filter = self.commuto_swap_contract.events.ResolutionProposed\
            .createFilter(fromBlock="latest",
                argument_filters = {
                    'swapID': newOfferID
                }
            )
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
        self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
        events = ResolutionProposed_event_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["swapID"], newOfferID)
        self.assertEqual(events[0]["args"]["disputeAgent"], self.dispute_agent_0)

    def test_proposeResolution_no_reaction_check(self):
        #Ensure resolution proposal can't be submitted if the maker or taker has already accepted or rejected
        try:
            newOfferID = HexBytes(uuid4().bytes)
            ReactionSubmitted_event_filter = self.commuto_swap_contract.events.ReactionSubmitted \
                .createFilter(fromBlock="latest",
                              argument_filters={
                                  'swapID': newOfferID
                              }
                              )
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_2
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
        except ValueError as e:
            # "e62": "A resolution proposal cannot be submitted if the maker or taker has already reacted"
            if not "e62" in str(e):
                raise e

