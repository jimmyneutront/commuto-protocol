// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

//Abstract ERC20 contract
abstract contract ERC20 {
  uint public totalSupply;

  event Transfer(address indexed from, address indexed to, uint value);
  event Approval(address indexed owner, address indexed spender, uint value);

  function balanceOf(address who) public view virtual returns (uint);
  function allowance(address owner, address spender) public view virtual returns (uint);

  function transfer(address to, uint value) public virtual returns (bool ok);
  function transferFrom(address from, address to, uint value) public virtual returns (bool ok);
  function approve(address spender, uint value) public virtual returns (bool ok);
}
