import CommutoSwapTest

class CommutoTokenTest(CommutoSwapTest.CommutoSwapTest):

    def test_changeTimelock_caller_is_timelock(self):
        #Ensure that changeTimelock cannot be called by any account other than Timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.CommutoToken_contract.functions.changeTimelock(
                self.w3.eth.accounts[2],
            ).transact(tx_details)
            raise Exception("test_changeTimelock_caller_is_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_changeTimelock_event_emission_check(self):
        #Ensure that changeTimelock emits TimelockChanged event upon successful change
        TimelockChanged_filter = self.CommutoToken_contract.events.TimelockChanged.createFilter(fromBlock="latest")
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.CommutoToken_contract.functions.changeTimelock(self.primary_timelock_contract.address).transact(tx_details)
        events = TimelockChanged_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["oldTimelock"], self.w3.eth.accounts[2])
        self.assertEqual(events[0]["args"]["newTimelock"], self.primary_timelock_contract.address)

    def test_mint_caller_is_primary_timelock(self):
        #Ensure that mint cannot be called by any account other than the primary timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.CommutoToken_contract.functions.mint(
                self.w3.eth.accounts[2],
                100,
            ).transact(tx_details)
            raise Exception("test_mint_caller_is_primary_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_burn_caller_is_primary_timelock(self):
        #Ensure that burn cannot be called by any account other than the primary timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.CommutoToken_contract.functions.burn(
                self.w3.eth.accounts[2],
                100,
            ).transact(tx_details)
            raise Exception("test_burn_caller_is_primary_timelock failed without raising exception")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            if not "e79" in str(e):
                raise e

    def test_changeRevenueCollectionPeriod_caller_is_timelock(self):
        #Ensure that changeRevenueCollectionPeriod cannot be called by any account other than Timelock
        try:
            tx_details = {
                "from": self.w3.eth.accounts[6],
            }
            self.CommutoToken_contract.functions.changeRevenueCollectionPeriod(
                100800,
            ).transact(tx_details)
            raise Exception("test_changeRevenueCollectionPeriod_caller_is_timelock: revert not received")
        except ValueError as e:
            # "e79": "Only the current primary timelock can call this function"
            self.assertTrue("e79" in str(e))

    def test_changeRevenueCollectionPeriod_event_emission_check(self):
        #Ensure that changeRevenueCollectionPeriod emits RevenueCollectionPeriodChanged event upon successful change
        RevenueCollectionPeriodChanged_filter = self.CommutoToken_contract.events.RevenueCollectionPeriodChanged\
            .createFilter(fromBlock="latest")
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.CommutoToken_contract.functions.changeRevenueCollectionPeriod(100800).transact(tx_details)
        events = RevenueCollectionPeriodChanged_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["args"]["oldPeriod"], 201600)
        self.assertEqual(events[0]["args"]["newPeriod"], 100800)

    def test_changeRevenueCollectionPeriod_ensure_new_period_is_set(self):
        #Ensure that changeRevenueCollectionPeriod sets the new period
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        self.CommutoToken_contract.functions.changeRevenueCollectionPeriod(100800).transact(tx_details)
        newPeriod = self.CommutoToken_contract.functions.getRevenueCollectionPeriod().call()
        self.assertEqual(newPeriod, 100800)
        
    def test_takeRevenueDistributionSnapshot_event_emission_check(self):
        #Ensure that takeRevenueDistributionSnapshot emits RevenueDistributionSnapshotTaken event upon successful call
        RevenueDistributionSnapshotTaken_filter = self.CommutoToken_contract.events.RevenueDistributionSnapshotTaken\
            .createFilter(fromBlock="latest")
        #Transfer some DAI to the Commuto Token contract
        self.test_dai_contract.functions.transfer(self.CommutoToken_contract.address, 100000)\
            .transact({'from': self.w3.eth.accounts[0]})
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        revenueCollectionPeriod = self.CommutoToken_contract.functions.getRevenueCollectionPeriod().call()
        self.mine_blocks(revenueCollectionPeriod)
        self.CommutoToken_contract.functions.takeRevenueDistributionSnapshot(self.test_dai_contract.address) \
            .transact(tx_details)
        events = RevenueDistributionSnapshotTaken_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertNotEqual(events[0]["args"]["snapshotId"], 0)
        self.assertEqual(events[0]["args"]["balance"], 100000)

    def test_takeRevenueDistributionSnapshot_new_period_is_set(self):
        #Ensure that takeRevenueDistributionSnapshot actually takes a snapshot
        self.test_dai_contract.functions.transfer(self.CommutoToken_contract.address, 100000) \
            .transact({'from': self.w3.eth.accounts[0]})
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        revenueCollectionPeriod = self.CommutoToken_contract.functions.getRevenueCollectionPeriod().call()
        self.mine_blocks(revenueCollectionPeriod)
        self.CommutoToken_contract.functions.takeRevenueDistributionSnapshot(self.test_dai_contract.address) \
            .transact(tx_details)
        snapshot = self.CommutoToken_contract.functions.getRevenueDistributionSnapshot(self.test_dai_contract.address)\
            .call()
        self.assertNotEqual(snapshot[0], 0)
        self.assertNotEqual(snapshot[1], 0)
        self.assertEqual(snapshot[2], 100000)

    def test_takeRevenueDistributionSnapshot_enforces_collection_period(self):
        #Ensure that takeRevenueDistributionSnapshot enforces the revenue collection period
        self.test_dai_contract.functions.transfer(self.CommutoToken_contract.address, 100000) \
            .transact({'from': self.w3.eth.accounts[0]})
        tx_details = {
            "from": self.w3.eth.accounts[2],
        }
        revenueCollectionPeriod = self.CommutoToken_contract.functions.getRevenueCollectionPeriod().call()
        self.mine_blocks(revenueCollectionPeriod)
        #This first call to takeRevenueDistributionSnapshot should succeed
        self.CommutoToken_contract.functions.takeRevenueDistributionSnapshot(self.test_dai_contract.address)\
            .transact(tx_details)
        try:
            #This second call should not, because the revenue collection period has not yet passed
            self.CommutoToken_contract.functions.takeRevenueDistributionSnapshot(self.test_dai_contract.address) \
                .transact(tx_details)
        except ValueError as e:
            self.assertTrue("e0" in str(e)) #"e0": "More blocks must be mined before a revenue distribution snapshot can be created"
        """
        Mine enough blocks to pass the revenue collection period, and then the following call to 
        takeRevenueDistributionSnapshot should succeed
        """
        revenueCollectionPeriod = self.CommutoToken_contract.functions.getRevenueCollectionPeriod().call()
        self.mine_blocks(revenueCollectionPeriod)
        #Set up a filter to make sure the snapshot is actually taken on this third attempt
        RevenueDistributionSnapshotTaken_filter = self.CommutoToken_contract.events.RevenueDistributionSnapshotTaken \
            .createFilter(fromBlock="latest")
        self.CommutoToken_contract.functions.takeRevenueDistributionSnapshot(self.test_dai_contract.address) \
            .transact(tx_details)
        events = RevenueDistributionSnapshotTaken_filter.get_new_entries()
        self.assertEqual(len(events), 1)
        self.assertNotEqual(events[0]["args"]["snapshotId"], 0)
        self.assertEqual(events[0]["args"]["balance"], 100000)