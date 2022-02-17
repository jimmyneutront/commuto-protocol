// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./CommutoSwapStorage.sol";

contract CommutoSwapPaymentReporter is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Report payment sent for swap
    /*
    This function should only be called by CommutoSwap's reportPaymentSent function. No attempt to report that payment
    for a swap has been sent by directly calling this method will succeed.
    */
    function reportPaymentSent(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(!swaps[swapID].requiresFill, "e48"); //"e48": "The swap must be filled before payment is sent"
        require(!swaps[swapID].isPaymentSent, "e34"); //"e34": "Payment sending has already been reported for swap with specified id"
        if(swaps[swapID].direction == SwapDirection.BUY) {
            require(swaps[swapID].maker == msg.sender, "e35"); //"e35": "Payment sending can only be reported by buyer"
        } else if (swaps[swapID].direction == SwapDirection.SELL) {
            require(swaps[swapID].taker == msg.sender, "e35"); //"e35": "Payment sending can only be reported by buyer"
        } else {
            revert("e36"); //"e36": "Swap has invalid direction"
        }

        //Mark payment sent and notify
        swaps[swapID].isPaymentSent = true;
        emit PaymentSent(swapID);
    }

    //Report payment received for swap
    /*
    This function should only be called by CommutoSwap's reportPaymentReceived function. No attempt to report that
    payment for a swap has been received by directly calling this method will succeed.
    */
    function reportPaymentReceived(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(swaps[swapID].isPaymentSent, "e37"); //"e37": "Payment sending has not been reported for swap with specified id"
        require(!swaps[swapID].isPaymentReceived, "e38"); //"e38": "Payment receiving has already been reported for swap with specified id"
        if(swaps[swapID].direction == SwapDirection.BUY) {
            require(swaps[swapID].taker == msg.sender, "e39"); //"e39": "Payment receiving can only be reported by seller"
        } else if (swaps[swapID].direction == SwapDirection.SELL) {
            require(swaps[swapID].maker == msg.sender, "e39"); //"e39": "Payment receiving can only be reported by seller"
        } else {
            revert("e36"); //"e36": "Swap has invalid direction"
        }

        //Mark payment received and notify
        swaps[swapID].isPaymentReceived = true;
        emit PaymentReceived(swapID);
    }

}
