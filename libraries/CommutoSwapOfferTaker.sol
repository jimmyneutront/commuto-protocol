// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";


contract CommutoSwapOfferTaker is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Take a swap offer
    /*
    This function should only be called by CommutoSwap's takeOffer function. No attempt to take an offer by directly
    calling this method will succeed.
    */
    function takeOffer(bytes16 offerID, Swap memory newSwap) public {
        //Validate arguments
        require(offers[offerID].isCreated, "e15"); //"e15": "An offer with the specified id does not exist",
        require(!swaps[offerID].isCreated, "e20"); //"e20": "The offer with the specified id has already been taken"
        require(offers[offerID].maker == newSwap.maker, "e21"); //"e21": "Maker addresses must match"
        require(sha256(offers[offerID].interfaceId) == sha256(newSwap.makerInterfaceId), "e21.1"); //"e21.1": "Maker interface ids must match",
        require(offers[offerID].stablecoin == newSwap.stablecoin, "e22"); //"e22": "Stablecoins must match"
        require(offers[offerID].amountLowerBound == newSwap.amountLowerBound, "e23"); //"e23": "Lower bounds must match"
        require(offers[offerID].amountUpperBound == newSwap.amountUpperBound, "e24"); //"e24": "Upper bounds must match"
        require(offers[offerID].securityDepositAmount == newSwap.securityDepositAmount, "e25"); //"e25": "Security deposit amounts must match"
        require(offers[offerID].amountLowerBound <= newSwap.takenSwapAmount, "e26"); //"e26": "Swap amount must be >= lower bound of offer amount"
        require(offers[offerID].amountUpperBound >= newSwap.takenSwapAmount, "e27"); //"e27": "Swap amount must be <= upper bound of offer amount"
        require(offers[offerID].direction == newSwap.direction, "e28"); //"e28": "Directions must match"
        require(sha256(offers[offerID].price) == sha256(newSwap.price), "e29"); //"e29": "Prices must match"
        require(settlementMethods[newSwap.settlementMethod] == true, "e46"); //"e46": "Settlement method must be supported"
        require(offerSettlementMethods[offerID][newSwap.settlementMethod] == true, "e30"); //"e30": "Settlement method must be accepted by maker"
        require(offers[offerID].protocolVersion == newSwap.protocolVersion, "e31"); //"e31": "Protocol versions must match"

        //Find proper stablecoin contract
        ERC20 token = ERC20(offers[offerID].stablecoin);

        //Calculate required total amount
        newSwap.serviceFeeAmount = SafeMath.div(newSwap.takenSwapAmount, 100);
        /*
        Slither complains that "totalAmount" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because a supported direction has not been specified.
        */
        uint256 totalAmount;
        if(newSwap.direction == SwapDirection.SELL) {
            //Taker is Buyer, maker is seller and must fill swap
            totalAmount = SafeMath.add(newSwap.securityDepositAmount, newSwap.serviceFeeAmount);
            newSwap.requiresFill = true;
        } else if (newSwap.direction == SwapDirection.BUY) {
            //Taker is seller, maker is buyer and does not need to fill swap
            totalAmount = SafeMath.add(SafeMath.add(newSwap.takenSwapAmount, newSwap.securityDepositAmount), newSwap.serviceFeeAmount);
            newSwap.requiresFill = false;
        } else {
            revert("e12"); //"e12": "You must specify a supported direction"
        }

        //Finish swap creation and notify that offer is taken
        newSwap.isCreated = true;
        newSwap.taker = msg.sender;
        offers[offerID].isTaken = true;
        newSwap.isPaymentSent = false;
        newSwap.isPaymentReceived = false;
        newSwap.hasBuyerClosed = false;
        newSwap.hasSellerClosed = false;
        swaps[offerID] = newSwap;
        emit OfferTaken(offerID, newSwap.takerInterfaceId);

        //Lock required total amount in escrow
        require(totalAmount <= token.allowance(msg.sender, address(this)), "e13"); //"e13": "Token allowance must be >= required amount"
        require(token.transferFrom(msg.sender, address(this), totalAmount), "e14"); //"e14": "Token transfer to Commuto Protocol failed"
    }

}
