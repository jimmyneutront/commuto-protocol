// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./SafeMath.sol";

/*
Contains the cancelOffer method, to which CommutoSwap delegates cancelOffer calls to cancel offers and return deposited
STBL to the offer maker. This contract holds nothing in its own storage; its method is intended for use via delegatecall
only, so offers cannot be canceled by calling CommutoSwapOfferCanceler directly.
*/
contract CommutoSwapOfferCanceler is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Cancel open swap offer
    /*
    This function should only be called by CommutoSwap's cancelOffer function. No attempt to cancel an offer by directly
    calling this method will succeed.
    */
    function cancelOffer(bytes16 offerID) public {
        //Validate arguments
        require(offers[offerID].isCreated, "e15"); //"e15": "An offer with the specified id does not exist"
        require(!offers[offerID].isTaken, "e16"); //"e16": "Offer is taken and cannot be mutated"
        require(offers[offerID].maker == msg.sender, "e17"); //"e17": "Offers can only be mutated by offer maker"

        //Find proper stablecoin contract
        ERC20 token = ERC20(offers[offerID].stablecoin);

        //Calculate total amount in escrow
        //TODO: Service fee calculated here
        uint256 serviceFeeAmountUpperBound = SafeMath.mul(offers[offerID].serviceFeeRate, SafeMath.div(offers[offerID].amountUpperBound, 10000));
        //uint256 serviceFeeAmountUpperBound = SafeMath.mul(offers[offerID].serviceFeeRate, SafeMath.div(offers[offerID].amountUpperBound, 10000));
        /*
        Slither complains that "totalAmount" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because the specified offer has an invalid direction.
        */

        uint256 depositAmount = SafeMath.add(offers[offerID].securityDepositAmount, serviceFeeAmountUpperBound);

        //Delete offer, refund STBL and notify
        delete offers[offerID];
        //Delete records of supported settlement methods
        for (uint i = 0; i < offers[offerID].settlementMethods.length; i++) {
            offerSettlementMethods[offerID][offers[offerID].settlementMethods[i]] = false;
        }
        emit OfferCanceled(offerID);
        require(token.transfer(offers[offerID].maker, depositAmount), "e19"); //"e19": "Token transfer failed"
    }

}
