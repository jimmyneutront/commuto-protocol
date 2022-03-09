import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

#Note: this should probably be moved to a CommutoReactToResolutionTest file
    # TODO: Ensure rejection immediately marks swap as escalated

    #Note: this should be moved to a CommutoCloseDisputedSwapTest file
    # TODO: Ensure disputed swap can only be paid out if both maker and taker agree
    # TODO: Ensure disputed swap can only be paid out once
    # TODO: Ensure paying out emits event

    #Note: this should probably be moved to a CommutoEscalateDisputeTest file
    # TODO: Ensure escalation can only be done by maker or taker
    # TODO: Ensure disputed swap can only be escalated to token holders given nonmatching response from dispute agents if > 1 week has passed
    # TODO: Ensure disputed swap can only be escalated to token holders given lack of response from maker if > 1 week has passed
    # TODO: Ensure disputed swap can only be escalated to token holders given lack of response from taker if > 1 week has passed

class CommutoReactToResolutionProposalTest(CommutoSwapTest.CommutoSwapTest):

    def test_reactToResolutionProposal_caller_is_maker_or_taker_check(self):
        #Ensure only maker or taker can react to resolution proposal
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            raise (Exception(
                "test_reactToResolutionProposal_caller_is_maker_or_taker_check failed without raising exception"))
        except ValueError as e:
            # "e57": "Only swap maker or taker can react to resolution proposal"
            if not "e57" in str(e):
                raise e

    def test_reactToResolutionProposal_not_no_reaction_check(self):
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 0).transact(tx_details)
            raise (Exception(
                "test_reactToResolutionProposal_not_no_reaction_check failed without raising exception"))
        except ValueError as e:
            # "e58": "Can't react with no reaction"
            if not "e58" in str(e):
                raise e

    def test_reactToResolutionProposal_maker_duplicate_call_prevention_check(self):
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            raise (Exception(
                "test_reactToResolutionProposal_maker_duplicate_call_prevention_check failed without raising exception"))
        except ValueError as e:
            #"e59": "Maker can't react to resolution proposal more than once"
            if not "e59" in str(e):
                raise e

    def test_reactToResolutionProposal_taker_duplicate_call_prevention_check(self):
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            raise (Exception(
                "test_reactToResolutionProposal_taker_duplicate_call_prevention_check failed without raising exception"))
        except ValueError as e:
            #"e60": "Maker can't react to resolution proposal more than once"
            if not "e60" in str(e):
                raise e

    def test_reactToResolutionProposal_matching_proposals_check(self):
        #Ensure maker or taker cannot accept or reject until at least two matching results have been submitted
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 99, 19, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_2
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 98, 20, 0).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
        except ValueError as e:
            #"e61": "Two matching resolutions must be proposed before reaction is allowed"
            if not "e61" in str(e):
                raise e

    def test_reactToResolutionProposal_event_emission_check(self):
        #Ensure reacting emits event
        newOfferID = HexBytes(uuid4().bytes)
        ReactionSubmitted_event_filter = self.commuto_swap_contract.events.ReactionSubmitted\
            .createFilter(fromBlock = "latest",
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
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_2
        }
        self.commuto_swap_contract.functions.proposeResolution(newOfferID, 100, 18, 0).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
        events = ReactionSubmitted_event_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["swapID"], newOfferID)
        self.assertEqual(events[0]["args"]["addr"], self.taker_address)
        self.assertEqual(events[0]["args"]["reaction"], 1)