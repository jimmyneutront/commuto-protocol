// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

/*
Contains Solidity types used by CommutoSwap
*/

enum SwapDirection  {
    BUY, //Maker has FIAT, wants STBL
    SELL //Maker has STBL, wants FIAT
}

enum DisputeRaiser  {
    NONE, //Swap is not disputed
    MAKER, //Maker raised dispute
    TAKER //Taker raised dispute
}

enum DisputeReaction {
    NO_REACTION, //Swapper hasn't reacted to resolution proposal yet
    ACCEPTED, //Swapper has accepted resolution proposal
    REJECTED //Swapper has rejected resolution proposal
}

enum DisputeState {
    OPEN, //Disputed swap is neither paid out nor escalated
    PAID_OUT, //Maker and taker both accepted dispute result and one of them called closeDisputedSwap
    ESCALATED //Maker and taker didn't both accept dispute result and one of them is escalating dispute to CMTO tokenholders
}

struct Offer {
    bool isCreated;
    bool isTaken;
    address maker;
    bytes interfaceId;
    address stablecoin;
    uint256 amountLowerBound;
    uint256 amountUpperBound;
    uint256 securityDepositAmount;
    SwapDirection direction;
    bytes price;
    bytes[] settlementMethods;
    uint256 protocolVersion;
}

struct Swap {
    bool isCreated;
    bool requiresFill;
    address maker;
    bytes makerInterfaceId;
    address taker;
    bytes takerInterfaceId;
    address stablecoin;
    uint256 amountLowerBound;
    uint256 amountUpperBound;
    uint256 securityDepositAmount;
    uint256 takenSwapAmount;
    uint256 serviceFeeAmount;
    SwapDirection direction;
    bytes price;
    bytes settlementMethod;
    uint256 protocolVersion;
    bool isPaymentSent;
    bool isPaymentReceived;
    bool hasBuyerClosed;
    bool hasSellerClosed;
    DisputeRaiser disputeRaiser;
}

struct Dispute {
    uint disputeRaisedBlockNum;
    address disputeAgent0;
    address disputeAgent1;
    address disputeAgent2;
    bool hasDA0Proposed;
    uint256 dA0MakerPayout;
    uint256 dA0TakerPayout;
    uint256 dA0ConfiscationPayout;
    bool hasDA1Proposed;
    uint256 dA1MakerPayout;
    uint256 dA1TakerPayout;
    uint256 dA1ConfiscationPayout;
    bool hasDA2Proposed;
    uint256 dA2MakerPayout;
    uint256 dA2TakerPayout;
    uint256 dA2ConfiscationPayout;
    DisputeReaction makerReaction;
    DisputeReaction takerReaction;
    DisputeState state;
    bool hasMakerPaidOut;
    bool hasTakerPaidOut;
}