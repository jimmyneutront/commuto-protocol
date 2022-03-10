import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

#TODO: Throw exception if smart contract call doesn't throw

class CommutoCloseDisputedSwapTest(CommutoSwapTest.CommutoSwapTest):

    def test_closeDisputedSwap_caller_is_maker_or_taker_check(self):
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_2
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_0
            }
            self.commuto_swap_contract.functions.closeDisputedSwap(newOfferID).transact(tx_details)
        except ValueError as e:
            # "e63": "Only maker and taker can close disputed swap"
            if not "e63" in str(e):
                raise e

    def test_closeDisputedSwap_maker_and_taker_accept_check(self):
        #Ensure disputed swap can only be paid out if both maker and taker agree
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_2
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.closeDisputedSwap(newOfferID).transact(tx_details)
        except ValueError as e:
            # "e64": "Disputed swap closure requires proposal acceptance by maker and taker"
            if not "e64" in str(e):
                raise e

    def test_closeDisputedSwap_maker_duplicate_call_check(self):
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_2
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.closeDisputedSwap(newOfferID).transact(tx_details)
            self.commuto_swap_contract.functions.closeDisputedSwap(newOfferID).transact(tx_details)
        except ValueError as e:
            # "e65": "Maker cannot pay out disputed swap more than once"
            if not "e65" in str(e):
                raise e

    def test_closeDisputedSwap_taker_duplicate_call_check(self):
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
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_1
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.dispute_agent_2
            }
            self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            self.commuto_swap_contract.functions.closeDisputedSwap(newOfferID).transact(tx_details)
            self.commuto_swap_contract.functions.closeDisputedSwap(newOfferID).transact(tx_details)
        except ValueError as e:
            # "e66": "Taker cannot pay out disputed swap more than once"
            if not "e66" in str(e):
                raise e

    def test_closeDisputedSwap_event_emission_check(self):
        #Ensure closing disputed swap emits event
        newOfferID = HexBytes(uuid4().bytes)
        DisputedSwapClosed_event_filter = self.commuto_swap_contract.events.DisputedSwapClosed\
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
        self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_1
        }
        self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
        tx_details = {
            "from": self.dispute_agent_2
        }
        self.commuto_swap_contract.functions.proposeResolution(newOfferID, 10, 10, 0).transact(tx_details)
        tx_details = {
            "from": self.maker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.reactToResolutionProposal(newOfferID, 1).transact(tx_details)
        tx_details = {
            "from": self.taker_address
        }
        self.commuto_swap_contract.functions.closeDisputedSwap(newOfferID).transact(tx_details)
        events = DisputedSwapClosed_event_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["swapID"], newOfferID)
        self.assertEqual(events[0]["args"]["closer"], self.taker_address)