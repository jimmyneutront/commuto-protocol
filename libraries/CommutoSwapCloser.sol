// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

/*
Contains the closeSwap method, to which CommutoSwap delegates closeSwap and closeDisputedSwap calls to mark swaps as
closed and complete STBL payment. This contract holds nothing in its own storage; its method is intended for use via
delegatecall only, so swaps cannot be closed by calling CommutoSwapCloser directly.
*/
contract CommutoSwapCloser is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Close swap and receive STBL from escrow
    /*
    This function should only be called by CommutoSwap's closeSwap function. No attempt close a swap by directly calling
    this method will succeed.
    */
    function closeSwap(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(swaps[swapID].isPaymentReceived, "e40"); //"e40": "Payment receiving has not been reported for swap with specified id"
        require(swaps[swapID].disputeRaiser == DisputeRaiser.NONE, "e52"); //"e52": "Swap cannot be closed if it is disputed"

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

    function closeDisputedSwap(bytes16 swapID) public {
        require(disputes[swapID].makerReaction == DisputeReaction.ACCEPTED && disputes[swapID].takerReaction == DisputeReaction.ACCEPTED, "e64"); //"e64": "Disputed swap closure requires proposal acceptance by maker and taker"

        //Find proper stablecoin contract
        ERC20 token = ERC20(swaps[swapID].stablecoin);

        //Find proper payout amounts
        uint256 makerPayout = 0;
        uint256 takerPayout = 0;
        uint256 confiscationPayout = 0;

        if (disputes[swapID].matchingProposals == MatchingProposalPair.ZERO_AND_ONE || disputes[swapID].matchingProposals == MatchingProposalPair.ZERO_AND_TWO) {
            makerPayout = disputes[swapID].dA0MakerPayout;
            takerPayout = disputes[swapID].dA0TakerPayout;
            confiscationPayout = disputes[swapID].dA0ConfiscationPayout;
        } else {
            makerPayout = disputes[swapID].dA1MakerPayout;
            takerPayout = disputes[swapID].dA1TakerPayout;
            confiscationPayout = disputes[swapID].dA1ConfiscationPayout;
        }

        //The last person to call this function must pay for the confiscated amount transfer
        bool mustPayConfiscationAmount = false;
        uint256 payoutAmountToCaller = 0;

        if (msg.sender == swaps[swapID].maker) {
            require(!disputes[swapID].hasMakerPaidOut, "e65"); //"e65": "Maker cannot close disputed swap more than once"
            payoutAmountToCaller = makerPayout;
            disputes[swapID].hasMakerPaidOut = true;
            if (disputes[swapID].hasTakerPaidOut == true) {
                //Caller is the final caller
                mustPayConfiscationAmount = true;
            }
        } else if (msg.sender == swaps[swapID].taker) {
            require(!disputes[swapID].hasTakerPaidOut, "e66"); //"e66": "Taker cannot close disputed swap more than once"
            payoutAmountToCaller = takerPayout;
            disputes[swapID].hasTakerPaidOut = true;
            if (disputes[swapID].hasMakerPaidOut == true) {
                //Caller is the final caller
                mustPayConfiscationAmount = true;
            }
        } else {
            revert("e63"); //"e63": "Only maker and taker can close disputed swap"
        }

        require(token.transfer(msg.sender, payoutAmountToCaller), "e19"); //"e19": "Token transfer failed"
        require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"

        if (mustPayConfiscationAmount == true) {
            require(token.transfer(serviceFeePool, confiscationPayout), "e67"); //"e67": "Confiscated amount transfer failed"
            //Caller is the final caller, so mark swap as paid out
            disputes[swapID].state = DisputeState.PAID_OUT;
        }

        emit DisputedSwapClosed(swapID, msg.sender);

    }

}
