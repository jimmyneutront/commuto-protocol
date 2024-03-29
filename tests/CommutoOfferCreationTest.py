import CommutoSwapTest
from hexbytes import HexBytes
from uuid import uuid4

class CommutoOfferCreationTest(CommutoSwapTest.CommutoSwapTest):

    def test_amountLowerBound_limit(self):
        try:
            tx_details = {
                "from": self.maker_address,
            }
            newOfferID = HexBytes(uuid4().bytes)
            newOffer = {
                "isCreated": True,
                "isTaken": True,
                "maker": self.maker_address,
                "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 0,
                "amountUpperBound": 10000,
                "securityDepositAmount": 1000,
                "serviceFeeRate": 100,
                "direction": 1,
                "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            raise (Exception("test_amountLowerBound_limit failed without raising exception"))
        except ValueError as e:
            # "e6":"The minimum swap amount must be greater than zero"
            if not "e6" in str(e):
                raise e

    def test_amountUpperBound_greater_than_or_equal_amountLowerBound(self):
        #amountUpperBound must be >= amountLowerBound
        try:
            tx_details = {
                "from": self.maker_address,
            }
            newOfferID = HexBytes(uuid4().bytes)
            newOffer = {
                "isCreated": True,
                "isTaken": True,
                "maker": self.maker_address,
                "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 2,
                "amountUpperBound": 1,
                "securityDepositAmount": 1000,
                "serviceFeeRate": 100,
                "direction": 1,
                "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            raise (Exception("test_amountUpperBound_greater_than_or_equal_amountLowerBound failed without raising "
                             "exception"))
        except ValueError as e:
            # "e7":"The maximum swap amount must be >= the minimum swap amount"
            if not "e7" in str(e):
                raise e

    def test_securityDepositAmount_sufficient(self):
        #securityDepositAmount must be at least 10% of amountLowerBound
        try:
            tx_details = {
                "from": self.maker_address,
            }
            newOfferID = HexBytes(uuid4().bytes)
            newOffer = {
                "isCreated": True,
                "isTaken": True,
                "maker": self.maker_address,
                "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 11000,
                "amountUpperBound": 100000,
                "securityDepositAmount": 900,
                "serviceFeeRate": 100,
                "direction": 1,
                "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            raise (Exception("test_securityDepositAmount_sufficient failed without raising exception"))
        except ValueError as e:
            # "e8":"The security deposit must be at least 10% of the maximum swap amount"
            if not "e8" in str(e):
                raise e

    def test_service_fee_sufficient(self):
        #service fee must be greater than zero
        try:
            tx_details = {
                "from": self.maker_address,
            }
            newOfferID = HexBytes(uuid4().bytes)
            newOffer = {
                "isCreated": True,
                "isTaken": True,
                "maker": self.maker_address,
                "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
                "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
                "amountLowerBound": 9000,
                "amountUpperBound": 10000,
                "securityDepositAmount": 1000,
                "serviceFeeRate": 100,
                "direction": 1,
                "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
                "protocolVersion": 1,
            }
            self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            raise (Exception("test_service_fee_sufficient failed without raising exception"))
        except ValueError as e:
            # "e9":"Service fee amount must be greater than zero"
            if not "e9" in str(e):
                raise e

    def test_zero_service_fee(self):
        #ensure the service fee can be zero when the service fee rate is zero
        tx_details = {
            "from": self.w3.eth.accounts[2]
        }
        self.commuto_swap_contract.functions.setServiceFeeRate(0).transact(tx_details)
        newOfferID = HexBytes(uuid4().bytes)
        tx_details = {
            "from": self.maker_address,
        }
        OfferOpened_event_filter = self.commuto_swap_contract.events.OfferOpened\
            .createFilter(fromBlock="latest",argument_filters={'offerID': newOfferID})
        newOffer = {
            "isCreated": True,
            "isTaken": True,
            "maker": self.maker_address,
            "interfaceId": HexBytes("an interface Id here".encode("utf-8").hex()),
            "stablecoin": self.dai_deployment_tx_receipt.contractAddress,
            "amountLowerBound": 10000,
            "amountUpperBound": 10000,
            "securityDepositAmount": 1000,
            "serviceFeeRate": 0,
            "direction": 1,
            "settlementMethods": ["USD-SWIFT|a price here".encode("utf-8"), ],
            "protocolVersion": 1,
        }
        self.test_dai_contract.functions.increaseAllowance(
            self.commuto_swap_deployment_tx_receipt.contractAddress,
            1000,
        ).transact(tx_details)
        self.commuto_swap_contract.functions.openOffer(
            newOfferID,
            newOffer,
        ).transact(tx_details)
        events = OfferOpened_event_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["offerID"], newOfferID)
        self.assertEqual(events[0]["args"]["interfaceId"], HexBytes("an interface Id here".encode("utf-8").hex()))
        self.assertEqual(events[0]["event"], "OfferOpened")

    # TODO: Test offer protocol check

    def test_openOffer_checks_STBL_allowance(self):
        #Ensure that openOffer checks for stablecoin allowance
        try:
            tx_details = {
                "from": self.maker_address,
            }
            newOfferID = HexBytes(uuid4().bytes)
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
            response = self.commuto_swap_contract.functions.openOffer(
                newOfferID,
                newOffer,
            ).transact(tx_details)
            print(response.hex())
            raise (Exception("test_openOffer_checks_STBL_allowance failed without raising exception"))
        except ValueError as e:
            # "e13":"Token allowance must be >= required amount"
            if not "e13" in str(e):
                raise e

    #TODO: Test for more event emissions

    def test_openOffer_emits_event(self):
        #Ensure openOffer emits OfferOpened event upon success
        try:
            newOfferID = HexBytes(uuid4().bytes)
            OfferOpened_event_filter = self.commuto_swap_contract.events.OfferOpened.createFilter(fromBlock="latest",
                                                                                             argument_filters={
                                                                                                 'offerID': newOfferID})
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
            events = OfferOpened_event_filter.get_new_entries()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["args"]["offerID"], newOfferID)
            self.assertEqual(events[0]["args"]["interfaceId"], HexBytes("an interface Id here".encode("utf-8").hex()))
            self.assertEqual(events[0]["event"], "OfferOpened")
        except ValueError as e:
            raise e

    def test_duplicate_offer_id_protection(self):
        #Ensure multiple offers cannot be created with the same id
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
                newOfferID,
                newOffer,
            ).transact(tx_details)
            raise (Exception("test_duplicate_offer_id_protection failed without raising exception"))
        except ValueError as e:
            # "e5":"An offer with the specified id already exists"
            if not "e5" in str(e):
                raise e