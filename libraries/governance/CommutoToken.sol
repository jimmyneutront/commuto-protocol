// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/extensions/draft-ERC20Permit.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";

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

    //Emitted when the old Timelock transfers control of CommutoToken to a new timelock
    event TimelockChanged(address oldTimelock, address newTimelock);
    //Emitted when the revenue collection period is changed
    event RevenueCollectionPeriodChanged(uint256 oldPeriod, uint256 newPeriod);
    //Emitted when a revenue distribution snapshot is taken
    event RevenueDistributionSnapshotTaken(address stablecoin, uint256 snapshotId, uint256 balance);

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
