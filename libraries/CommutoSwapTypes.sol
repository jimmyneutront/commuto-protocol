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
}