// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/extensions/draft-ERC20Permit.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";
import "../../node_modules/@openzeppelin/contracts/utils/math/SafeMath.sol";

contract CommutoToken is ERC20, ERC20Permit, ERC20Votes, ERC20Snapshot {
    constructor() ERC20("CommutoToken", "CMTO") ERC20Permit("CommutoToken") {
        timelock = msg.sender;
    }

    struct RevenueDistributionSnapshot {
        uint256 block;
        uint256 snapshotId;
        uint256 balance;
    }
    //A mapping of stablecoin contract addresses to the most recent revenue distribution snapshot for that stablecoin
    mapping (address => RevenueDistributionSnapshot) revenueDistributionSnapshots;
    //The address of the Timelock that shall be able to mint and burn CMTO and transfer control to another Timelock
    address public timelock;
    //The number of blocks that must be mined between snapshot creations for a particular stablecoin
    uint256 public revenueCollectionPeriod = 201600; // 1 week on BSC
    /*
    The block number at which the caller most recently collected revenue for the stablecoin with the contract address
    supplied as the first key
    */
    mapping (address => mapping(address => uint256)) latestRevenueCollection;

    //Emitted when the old Timelock transfers control of CommutoToken to a new timelock
    event TimelockChanged(address oldTimelock, address newTimelock);
    //Emitted when the revenue collection period is changed
    event RevenueCollectionPeriodChanged(uint256 oldPeriod, uint256 newPeriod);
    //Emitted when a revenue distribution snapshot is taken
    event RevenueDistributionSnapshotTaken(address stablecoin, uint256 snapshotId, uint256 balance);
    //Emitted when revenue is collected
    event RevenueCollected(address stablecoin, address collector, address recipient, uint256 amount);

    //Create a new revenue distribution snapshot for a specific stablecoin
    function takeRevenueDistributionSnapshot(address stablecoin) public {
        require(revenueDistributionSnapshots[stablecoin].block + revenueCollectionPeriod < block.number, "e0"); //"e0": "More blocks must be mined before a revenue distribution snapshot can be created"
        revenueDistributionSnapshots[stablecoin].block = block.number;

        //Create a new snapshot of CMTO holder balances and save it in the Revenue Distribution Snapshot
        uint256 newShapshotId = super._snapshot();
        revenueDistributionSnapshots[stablecoin].snapshotId = newShapshotId;

        //Get the balance of the specified stablecoin held by this contract and update
        ERC20 Stablecoin = ERC20(stablecoin);
        uint256 balance = Stablecoin.balanceOf(address(this));
        revenueDistributionSnapshots[stablecoin].balance = balance;

        emit RevenueDistributionSnapshotTaken(stablecoin, newShapshotId, balance);
    }

    function getRevenueDistributionSnapshot(address stablecoin) view public returns (RevenueDistributionSnapshot memory) {
        return revenueDistributionSnapshots[stablecoin];
    }

    //Collect revenue earned by the Commuto Protocol
    function collectRevenue(address stablecoin, address recipient) public {
        //Ensure the caller hasn't already collected revenue during this period
        RevenueDistributionSnapshot memory latestSnapshot = revenueDistributionSnapshots[stablecoin];
        require(latestRevenueCollection[stablecoin][msg.sender] < latestSnapshot.block, "e84"); //"e84": "More blocks must be mined before revenue can be collected again"

        //Get the caller's CMTO balance and the total supply at the latest snapshot
        uint256 callerCMTOBalance = super.balanceOfAt(msg.sender, latestSnapshot.snapshotId);
        uint256 totalSupply = super.totalSupplyAt(latestSnapshot.snapshotId);

        //Calculate the amount of revenue owed to the caller
        uint256 revenueOwed = SafeMath.div(SafeMath.mul(SafeMath.div(SafeMath.mul(callerCMTOBalance, 100_000_000), totalSupply), latestSnapshot.balance), 100_000_000);

        //emit RevenueCollected(stablecoin, msg.sender, recipient, revenueOwed);
        emit RevenueCollected(stablecoin, msg.sender, recipient, revenueOwed);

        //Update the caller's block number of latest collection
        latestRevenueCollection[stablecoin][msg.sender] = block.number;

        //Transfer the amount of revenue owed to the address specified by the caller
        ERC20 Stablecoin = ERC20(stablecoin);
        require(Stablecoin.transfer(recipient, revenueOwed), "e19"); //"e19": "Token transfer failed"
    }

    function getLatestRevenueCollection(address stablecoin, address account) view public returns (uint256) {
        return latestRevenueCollection[stablecoin][account];
    }

    //Transfer control of CommutoToken to a new timelock
    function changeTimelock(address newTimelock) public {
        require(msg.sender == timelock, "e79"); //"e79": "Only the current Timelock can call this function"
        emit TimelockChanged(timelock, newTimelock);
        timelock = newTimelock;
    }

    //Change the revenue collection period
    function changeRevenueCollectionPeriod(uint256 newRevenueCollectionPeriod) public {
        require(msg.sender == timelock, "e79"); //"e79": "Only the current Timelock can call this function"
        emit RevenueCollectionPeriodChanged(revenueCollectionPeriod, newRevenueCollectionPeriod);
        revenueCollectionPeriod = newRevenueCollectionPeriod;
    }

    function getRevenueCollectionPeriod() public view returns (uint256) {
        return revenueCollectionPeriod;
    }

    //Mint function
    function mint(address to, uint256 amount) public {
        require(msg.sender == timelock, "e79"); //"e79": "Only the current Timelock can call this function"
        _mint(to, amount);
    }

    //Burn function
    function burn(address account, uint256 amount) public {
        require(msg.sender == timelock, "e79"); //"e79": "Only the current Timelock can call this function"
        _burn(account, amount);
    }

    //Overrides required by Solidity

    function _beforeTokenTransfer(address from, address to, uint256 amount) internal override(ERC20, ERC20Snapshot) {
        super._beforeTokenTransfer(from, to, amount);
    }

    function _afterTokenTransfer(address from, address to, uint256 amount) internal override(ERC20, ERC20Votes) {
        super._afterTokenTransfer(from, to, amount);
    }

    function _mint(address to, uint256 amount) internal override(ERC20, ERC20Votes) {
        super._mint(to, amount);
    }

    function _burn(address account, uint256 amount) internal override(ERC20, ERC20Votes) {
        super._burn(account, amount);
    }

}
