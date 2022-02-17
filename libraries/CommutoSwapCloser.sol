// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

contract CommutoSwapCloser is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Close swap and receive STBL from escrow
    /*
    This function should only be called by CommutoSwap's closeSwap function. No attempt close a swap by directly calling
    this method will succeed.
    */
    function closeSwap(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(swaps[swapID].isPaymentReceived, "e40"); //"e40": "Payment receiving has not been reported for swap with specified id"

        //Find proper stablecoin contract
        ERC20 token = ERC20(swaps[swapID].stablecoin);

        uint256 returnAmount;

        //If caller is buyer and taker, return security deposit and swap amount, and send service fee to pool
        if(swaps[swapID].direction == SwapDirection.SELL && swaps[swapID].taker == msg.sender) {
            require(!swaps[swapID].hasBuyerClosed, "e41"); //"e41": "Buyer has already closed swap"
            returnAmount = SafeMath.add(swaps[swapID].securityDepositAmount, swaps[swapID].takenSwapAmount);
            swaps[swapID].hasBuyerClosed = true;
            emit BuyerClosed(swapID);
            require(token.transfer(swaps[swapID].taker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        }
        //If caller is buyer and maker, return security deposit, swap amount, and serviceFeeUpperBound - serviceFeeAmount, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.BUY && swaps[swapID].maker == msg.sender) {
            require(!swaps[swapID].hasBuyerClosed, "e41"); //"e41": "Buyer has already closed swap"
            uint256 serviceFeeAmountUpperBound = SafeMath.div(swaps[swapID].amountUpperBound, 100);
            returnAmount = SafeMath.add(SafeMath.add(swaps[swapID].securityDepositAmount, swaps[swapID].takenSwapAmount), SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount));
            swaps[swapID].hasBuyerClosed = true;
            emit BuyerClosed(swapID);
            require(token.transfer(swaps[swapID].maker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        }
        //If caller is seller and taker, return security deposit, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.BUY && swaps[swapID].taker == msg.sender) {
            require(!swaps[swapID].hasSellerClosed, "e43"); //"e43": "Seller has already closed swap"
            returnAmount = swaps[swapID].securityDepositAmount;
            swaps[swapID].hasSellerClosed = true;
            emit SellerClosed(swapID);
            require(token.transfer(swaps[swapID].taker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        }
        //If caller is seller and maker, return security deposit and serviceFeeUpperBound - serviceFeeAmount, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.SELL && swaps[swapID].maker == msg.sender) {
            require(!swaps[swapID].hasSellerClosed, "e43"); //"e43": "Seller has already closed swap"
            uint256 serviceFeeAmountUpperBound = SafeMath.div(swaps[swapID].amountUpperBound, 100);
            returnAmount = SafeMath.add(swaps[swapID].securityDepositAmount, SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount));
            swaps[swapID].hasSellerClosed = true;
            emit SellerClosed(swapID);
            require(token.transfer(swaps[swapID].maker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        } else {
            revert("e44"); //"e44": "Only swap maker or taker can call this function"
        }
    }

}
