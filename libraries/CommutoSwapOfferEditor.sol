// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./CommutoSwapStorage.sol";

/*
Contains the editOffer method, to which CommutoSwap delegates editOffer calles to change an offers's supported
settlement methods and price. This contract holds nothing in its own storage; its method is intended for use via
delegatecall only, so offers cannot be edited by calling CommutoSwapOfferEditor directly.
*/
contract CommutoSwapOfferEditor is CommutoSwapStorage{

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Edit the price and supported settlement methods of an open swap offer
    /*
    This function should only be called by CommutoSwap's editOffer function. No attempt to edit an offer by directly
    calling this method will succeed.
    */
    function editOffer(bytes16 offerID, Offer memory editedOffer, bool editPrice, bool editSettlementMethods) public {
        //Validate arguments
        require(offers[offerID].isCreated, "e15"); //"e15": "An offer with the specified id does not exist"
        require(!offers[offerID].isTaken, "e16"); //"e16": "Offer is taken and cannot be mutated"
        require(offers[offerID].maker == msg.sender, "e17"); //"e17": "Offers can only be mutated by offer maker"

        if (editPrice) {
            offers[offerID].price = editedOffer.price;
        }

        if (editSettlementMethods) {
            //Delete records of supported settlement methods in preparation for updated info
            for (uint i = 0; i < offers[offerID].settlementMethods.length; i++) {
                offerSettlementMethods[offerID][offers[offerID].settlementMethods[i]] = false;
            }
            //Record new supported settlement methods
            for (uint i = 0; i < editedOffer.settlementMethods.length; i++) {
                offerSettlementMethods[offerID][editedOffer.settlementMethods[i]] = true;
            }
            offers[offerID].settlementMethods = editedOffer.settlementMethods;
        }
    }

}
