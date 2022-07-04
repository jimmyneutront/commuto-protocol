import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoEditOfferTest(CommutoSwapTest.CommutoSwapTest):

    def test_editOffer_existence_check(self):
        #Ensure editOffer checks for offer existence
        try:
            tx_details = {
                "from": self.maker_address
            }
            editedOffer = {
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
            self.commuto_swap_contract.functions.editOffer(
                uuid4().bytes,
                editedOffer,
            ).transact(tx_details)
            raise (Exception("test_editOffer_existence_check failed without raising exception"))
        except ValueError as e:
            # "e15": "An offer with the specified id does not exist"
            if not "e15" in str(e):
                raise e

    def test_editOffer_taken_offer_check(self):
        #Ensuring editOffer checks that offer is not taken
        try:
            newOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address,
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
                newOfferID,
                newSwap,
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            editedOffer = {
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
            self.commuto_swap_contract.functions.editOffer(
                newOfferID,
                editedOffer,
            ).transact(tx_details)
            raise (Exception("test_editOffer_taken_offer_check failed without raising exception"))
        except ValueError as e:
            # "e16": "Offer is taken and cannot be mutated"
            if not "e16" in str(e):
                raise e

    def test_editOffer_caller_is_maker_check(self):
        #Ensure editOffer can only be called by offer maker
        try:
            newOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address
            }
            offerToEdit = {
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
                newOfferID,
                offerToEdit,
            ).transact(tx_details)
            tx_details = {
                "from": self.taker_address
            }
            editedOffer = {
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
            self.commuto_swap_contract.functions.editOffer(
                newOfferID,
                editedOffer,
            ).transact(tx_details)
            raise (Exception("test_editOffer_caller_is_maker_check failed without raising exception"))
        except ValueError as e:
            # "e17": "Offers can only be mutated by offer maker"
            if not "e17" in str(e):
                raise e

    def test_editOffer_edit_offer(self):
        #Ensure editOffer actually edits the offer
        try:
            newOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.maker_address
            }
            offerToEdit = {
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
                newOfferID,
                offerToEdit,
            ).transact(tx_details)
            tx_details = {
                "from": self.maker_address
            }
            editedOffer = {
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
                "settlementMethods": ["EUR-SEPA|an edited price here".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            OfferEdited_event_filter = self.commuto_swap_contract.events.OfferEdited.createFilter(
                fromBlock="latest",
                argument_filters={
                    "offerID": newOfferID
                }
            )
            self.commuto_swap_contract.functions.editOffer(
                newOfferID,
                editedOffer,
            ).transact(tx_details)
            events = OfferEdited_event_filter.get_new_entries()
            if not (len(events) == 1 and events[0]["args"]["offerID"] == newOfferID and
                    events[0]["event"] == "OfferEdited"):
                raise Exception("OfferEdited event for offer with id " + str(newOfferID) + " not found")
            offer = self.commuto_swap_contract.functions.getOffer(
                newOfferID,
            ).call()
            if not (offer[10] == ["EUR-SEPA|an edited price here".encode("utf-8"), ]):
                raise (Exception("test_editOffer_edit_offer failed due to offer editing failure"))
        except ValueError as e:
            raise e