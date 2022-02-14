// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

library CommutoNewOfferValidator {

    function validateNewOffer(Offer memory newOffer, uint256 protocolVersion) view public returns (Offer memory, uint256){
        //Validate arguments
        require(newOffer.amountLowerBound > 0, "e6"); //"The minimum swap amount must be greater than zero"
        require(newOffer.amountUpperBound >= newOffer.amountLowerBound, "e7"); //"e7": "The maximum swap amount must be >= the minimum swap amount"
        require(SafeMath.mul(newOffer.securityDepositAmount, 10) >= newOffer.amountUpperBound, "e8"); //"e8": "The security deposit must be at least 10% of the maximum swap amount"
        uint256 serviceFeeAmountLowerBound = SafeMath.div(newOffer.amountLowerBound, 100);
        require(serviceFeeAmountLowerBound > 0, "e9"); //"e9": "Service fee amount must be greater than zero"
        require(newOffer.protocolVersion >= protocolVersion, "e10"); //"e10": "Offers can only be created for the most recent protocol version"
        require(newOffer.direction == SwapDirection.BUY || newOffer.direction == SwapDirection.SELL, "e12"); //"e12": "You must specify a supported direction"

        //Calculate currently required deposit amount
        uint256 serviceFeeAmountUpperBound = SafeMath.div(newOffer.amountUpperBound, 100);
        uint256 depositAmount = SafeMath.add(newOffer.securityDepositAmount, serviceFeeAmountUpperBound);

        //Set offer properties
        newOffer.isCreated = true;
        newOffer.isTaken = false;
        newOffer.maker = msg.sender;

        return (newOffer, depositAmount);
    }

}
