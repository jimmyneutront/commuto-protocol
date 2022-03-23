// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/extensions/draft-ERC20Permit.sol";
import "../../node_modules/@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";

//TODO: Restrict new token minting to governance contract
contract CommutoToken is ERC20, ERC20Permit, ERC20Votes {
    constructor() ERC20("CommutoToken", "CMTO") ERC20Permit("CommutoToken") {
        timelock = msg.sender;
    }

    //The address of the Timelock that shall be able to mint and burn CMTO and transfer control to another Timelock
    address public timelock;

    //Emitted when the old Timelock transfers control of CommutoToken to a new timelock
    event TimelockChanged(address oldTimelock, address newTimelock);

    //Transfer control of CommutoToken to a new timelock
    function changeTimelock(address newTimelock) public {
        require(msg.sender == timelock, "e79"); //"e79": "Only the current Timelock can call this function"
        emit TimelockChanged(timelock, newTimelock);
        timelock = newTimelock;
    }

    //TODO: Mint function

    //TODO: Burn function

    //Overrides required by Solidity

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
