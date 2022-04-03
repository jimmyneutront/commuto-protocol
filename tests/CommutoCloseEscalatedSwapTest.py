import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoCloseEscalatedSwapTest(CommutoSwapTest.CommutoSwapTest):

    def test_closeEscalatedSwap_caller_is_timelock(self):
        #Ensure the caller of closeEscalatedSwap is the timelock
        try:
            nonExistentOfferID = HexBytes(uuid4().bytes)
            tx_details = {
                "from": self.w3.eth.accounts[6]
            }
            self.commuto_swap_contract.functions.closeEscalatedSwap(nonExistentOfferID, 1000, 500, 500).transact(tx_details)
        except ValueError as e:
            self.assertTrue("e79" in str(e))

    def test_closeEscalatedSwap_duplicate_call_check(self):
        """
        Ensure that closeEscalatedSwap cannot be called on a non-escalated swap. Note that this ensures that a swap
        cannot be closed more than once, since a closed swap is no longer marked as escalated. It also ensures that a
        non-existent swap cannot be closed, since a non-existent swap cannot be marked as escalated.
        """
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
            self.mine_blocks(5)
            tx_details = {
                "from": self.maker_address
            }
            self.commuto_swap_contract.functions.escalateDispute(newOfferID, 1).transact(tx_details)
            tx_details = {
                "from": self.w3.eth.accounts[2],
            }
            self.commuto_swap_contract.functions.closeEscalatedSwap(newOfferID, 1000, 500, 500).transact(tx_details)
            self.commuto_swap_contract.functions.closeEscalatedSwap(newOfferID, 500, 500, 1000).transact(tx_details)
        except ValueError as e:
            # "e70": "closeEscalatedSwap can only be called for escalated swaps"
            self.assertTrue("e70" in str(e))