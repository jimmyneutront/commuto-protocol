// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

/*
Contains the fillSwap method, to which CommutoSwap delegates fillSwap calls in order to accept STBL deposit equal to the
taken swap amount from the maker in maker-as-seller swaps. This contract holds nothing in its own storage; its method is
intended for use via delegatecall only, so swaps cannot be filled by calling CommutoSwapFiller directly.
*/
contract CommutoSwapFiller is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Fill swap (deposit takenSwapAmount of STBL) as maker and seller
    /*
    This function should only be called by CommutoSwap's fillSwap function. No attempt to fill a swap by directly
    calling this method will succeed.
    */
    function fillSwap(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(swaps[swapID].requiresFill && swaps[swapID].direction == SwapDirection.SELL, "e18"); //"e18": "Swap does not require filling"
        require(swaps[swapID].maker == msg.sender, "e47"); //"e47": "Only maker and seller can fill swap"
        require(swaps[swapID].disputeRaiser == DisputeRaiser.NONE, "e32"); //"e32": "Maker-as-seller swap cannot be filled if swap is disputed"

        //Update swap state
        swaps[swapID].requiresFill = false;
        emit SwapFilled(swapID);

        //Find proper stablecoin contract
        ERC20 token = ERC20(swaps[swapID].stablecoin);

        //Lock taken swap amount in escrow
        require(swaps[swapID].takenSwapAmount <= token.allowance(msg.sender, address(this)), "e13"); //"e13": "Token allowance must be >= required amount"
        require(token.transferFrom(msg.sender, address(this), swaps[swapID].takenSwapAmount), "e14"); //"e14": "Token transfer to Commuto Protocol failed"
    }

}
