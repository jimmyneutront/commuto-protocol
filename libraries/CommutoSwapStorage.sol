// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

import "./CommutoSwapTypes.sol";

/*
Establishes the contract storage layout for CommutoSwap and all the contracts to which CommutoSwap delegates calls
*/
contract CommutoSwapStorage {

    address public owner = address(0);
    address public serviceFeePool = address(0);

    //Address to which funds for escalated disputed swaps are sent until tokenholders approve a resolution
    address public escalatedDisputedSwapsPool = address(0);

    //Address of the contract to which CommutoSwap should delegate openOffer calls
    address immutable public commutoSwapOfferOpener;

    //Address of the contract to which CommutoSwap should delegate editOffer calls
    address immutable public commutoSwapOfferEditor;

    //Address of the contract to which CommutoSwap should delegate cancelOffer calls
    address immutable public commutoSwapOfferCanceler;

    //Address of the contract to which CommutoSwap should delegate takeOffer calls
    address immutable public commutoSwapOfferTaker;

    //Address of the contract to which CommutoSwap should delegate fillSwap calls
    address immutable public commutoSwapFiller;

    //Address of the contract to which CommutoSwap should delegate reportPaymentSent and reportPaymentReceived calls
    address immutable public commutoSwapPaymentReporter;

    //Address of the contract to which CommutoSwap should delegate closeSwap calls
    address immutable public commutoSwapCloser;

    //The number of blocks that must be mined between when a dispute is raised and when it can be escalated
    //TODO: Make this changeable by governance vote
    uint256 public minimumDisputePeriod = 5;

    //The current version of the Commuto Protocol
    uint256 public protocolVersion = 0;

    /*
    A mapping of settlement method names to boolean values indicating whether they are supported or not, and an array
    containing the names of all supported settlement methods. Both a mapping and an array are necessary because map
    value lookups are inexpensive and keep user costs down, but an array is necessary so that one can always obtain a
    complete list of supported settlement methods.
    */
    mapping (bytes => bool) internal settlementMethods;
    bytes[] internal supportedSettlementMethods;

    /*
    A mapping of stablecoin contract addresses to boolean values indicating whether they are supported or not, and an
    array containing the contract addresses of all supported stablecoins.
    */
    mapping (address => bool) internal stablecoins;
    address[] internal supportedStablecoins;

    /*
    A mapping of dispute agent addresses to boolean values indicating whether they are active or not, and an array
    containing the addresses of all active dispute agents.
    */
    mapping (address => bool) internal disputeAgents;
    address[] internal activeDisputeAgents;

    event OfferOpened(bytes16 offerID, bytes interfaceId);
    event PriceChanged(bytes16 offerID);
    event OfferCanceled(bytes16 offerID);
    event OfferTaken(bytes16 offerID, bytes takerInterfaceId);
    event SwapFilled(bytes16 swapID);
    event PaymentSent(bytes16 swapID);
    event PaymentReceived(bytes16 swapID);
    event BuyerClosed(bytes16 swapID);
    event SellerClosed(bytes16 swapID);
    event DisputeRaised(bytes16 swapID, address disputeAgent0, address disputeAgent1, address disputeAgent2);
    event ResolutionProposed(bytes16 swapID, address disputeAgent);
    event ReactionSubmitted(bytes16 swapID, address addr, DisputeReaction reaction);
    event DisputedSwapClosed(bytes16 swapID, address closer);
    event DisputeEscalated(bytes16 swapID, address escalator, EscalationReason reason);

    /*
    Mappings containing all offers, the settlement methods of each offer, and all swaps.
    */
    mapping (bytes16 => Offer) internal offers;
    mapping (bytes16 => mapping (bytes => bool)) internal offerSettlementMethods;
    mapping (bytes16 => Swap) internal swaps;

    /*
    Mapping containing the disputes for each disputed swap.
    */
    mapping (bytes16 => Dispute) internal disputes;

    constructor(address offerOpener, address offerEditor, address offerCanceler, address offerTaker, address swapFiller, address paymentReporter, address swapCloser) public {
        commutoSwapOfferOpener = offerOpener;
        commutoSwapOfferEditor = offerEditor;
        commutoSwapOfferCanceler = offerCanceler;
        commutoSwapOfferTaker = offerTaker;
        commutoSwapFiller = swapFiller;
        commutoSwapPaymentReporter = paymentReporter;
        commutoSwapCloser = swapCloser;
    }

}
