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
    ESCALATED, //Maker and taker didn't both accept dispute result and one of them is escalating dispute to CMTO tokenholders
    ESCALATED_PAID_OUT //A proposal was approved and executed and the swap is completed
}

enum MatchingProposalPair {
    NO_MATCH, //A pair of matching proposals hasn't yet been found
    ZERO_AND_ONE, //Proposals from dispute agents zero and one match
    ZERO_AND_TWO, //Proposals from dispute agents zero and two match
    ONE_AND_TWO //Proposals from dispute agents one and two match
}

enum EscalationReason {
    REJECTION, //Escalating the swap because the maker or taker has rejected the dispute agents' proposal
    NO_DISPUTE_AGENT_AGREEMENT, //Escalating the swap because the dispute agents didn't agree on a proposal
    NO_COUNTERPARTY_REACTION //Escalating the swap because the counterparty didn't react
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
    uint256 serviceFeeRate;
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
    uint256 serviceFeeRate;
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
    MatchingProposalPair matchingProposals;
    DisputeReaction makerReaction;
    DisputeReaction takerReaction;
    DisputeState state;
    bool hasMakerPaidOut;
    bool hasTakerPaidOut;
    uint256 totalWithoutSpentServiceFees;
}