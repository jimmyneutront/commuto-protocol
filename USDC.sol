// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.0/contracts/token/ERC20/ERC20.sol";

contract USDC is ERC20 {
    constructor () public ERC20("Dai", "DAI") {
    }
    function mint(address account, uint256 amount) public {
        _mint(account, amount);
    }
}