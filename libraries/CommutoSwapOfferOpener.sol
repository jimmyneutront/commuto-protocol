// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;
//import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.0/contracts/math/SafeMath.sol";
import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

contract CommutoSwapOfferOpener is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0)) public {}

    //Create a new swap offer
    /*
    This function should only be called by CommutoSwap's openOffer function. No offer opened by directly calling this
    function can be completed.
    Note that openOffer will not prevent a maker from creating an offer with unsupported settlement methods, to keep gas
    costs low. However, a taker will not be able to take an offer with unsupported settlement methods, so the maker
    should be careful not to create such invalid offers.
    */
    function openOffer(bytes16 offerID, Offer memory newOffer) public {
        //Validate arguments
        require(!offers[offerID].isCreated, "e5"); //"An offer with the specified id already exists"
        require(newOffer.amountLowerBound > 0, "e6"); //"The minimum swap amount must be greater than zero"
        require(newOffer.amountUpperBound >= newOffer.amountLowerBound, "e7"); //"e7": "The maximum swap amount must be >= the minimum swap amount"
        require(SafeMath.mul(newOffer.securityDepositAmount, 10) >= newOffer.amountUpperBound, "e8"); //"e8": "The security deposit must be at least 10% of the maximum swap amount"
        uint256 serviceFeeAmountLowerBound = SafeMath.div(newOffer.amountLowerBound, 100);
        require(serviceFeeAmountLowerBound > 0, "e9"); //"e9": "Service fee amount must be greater than zero"
        require(newOffer.protocolVersion >= protocolVersion, "e10"); //"e10": "Offers can only be created for the most recent protocol version"
        require(newOffer.direction == SwapDirection.BUY || newOffer.direction == SwapDirection.SELL, "e12"); //"e12": "You must specify a supported direction"

        //Find proper stablecoin contract
        /*
        Slither complains that "token" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because a supported stablecoin has not been specified.
        */
        ERC20 token;

        if(stablecoins[newOffer.stablecoin] == true) {
            token = ERC20(newOffer.stablecoin);
        } else {
            revert("e11");
        }

        //Calculate currently required deposit amount
        uint256 serviceFeeAmountUpperBound = SafeMath.div(newOffer.amountUpperBound, 100);
        /*
        Slither complains that "totalAmount" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because a supported direction has not been specified.
        */

        uint256 depositAmount = SafeMath.add(newOffer.securityDepositAmount, serviceFeeAmountUpperBound);

        /*
        uint256 totalAmount;
        if(newOffer.direction == SwapDirection.SELL) {
            totalAmount = SafeMath.add(SafeMath.add(newOffer.amountUpperBound, newOffer.securityDepositAmount), serviceFeeAmountUpperBound);
        } else if (newOffer.direction == SwapDirection.BUY) {
            totalAmount = SafeMath.add(newOffer.securityDepositAmount, serviceFeeAmountUpperBound);
        } else {
            revert("e12"); //"e12": "You must specify a supported direction"
        }*/

        //Finish and notify of offer creation
        newOffer.isCreated = true;
        newOffer.isTaken = false;
        newOffer.maker = msg.sender;
        offers[offerID] = newOffer;
        //Record supported settlement methods
        for (uint i = 0; i < newOffer.settlementMethods.length; i++) {
            offerSettlementMethods[offerID][newOffer.settlementMethods[i]] = true;
        }
        emit OfferOpened(offerID, newOffer.interfaceId);

        //Lock required total amount in escrow
        require(depositAmount <= token.allowance(msg.sender, address(this)), "e13"); //"e13": "Token allowance must be >= required amount"
        require(token.transferFrom(msg.sender, address(this), depositAmount), "e14"); //"e14": "Token transfer to Commuto Protocol failed"
    }
}
