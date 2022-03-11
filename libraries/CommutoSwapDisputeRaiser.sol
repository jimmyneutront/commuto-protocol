// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

/*
Contains the raiseDispute method, to which CommutoSwap delegates raiseDispute calls to raise disputes. This contract
holds nothing in its own storage; its method is intended only for use via delegatecall, so disputes cannot be raised by
calling CommutoSwapDisputeRaiser directly.
*/
contract CommutoSwapDisputeRaiser is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Raise a dispute for a swap
    /*
    This function should only be called by CommutoSwap's raiseDispute function. No attempt raise a dispute by directly
    calling this method will succeed.
    */
    function raiseDispute(bytes16 swapID, address disputeAgent0, address disputeAgent1, address disputeAgent2) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(disputeAgents[disputeAgent0], "e3"); //"e3": "Selected dispute agents must be active"
        require(disputeAgents[disputeAgent1], "e3"); //"e3": "Selected dispute agents must be active"
        require(disputeAgents[disputeAgent2], "e3"); //"e3": "Selected dispute agents must be active"
        require(!swaps[swapID].hasBuyerClosed && !swaps[swapID].hasSellerClosed, "e4"); //"e4": "Dispute cannot be raised if maker or taker has already closed"
        require(swaps[swapID].disputeRaiser == DisputeRaiser.NONE, "e53"); //"e53": "Dispute cannot be raised for an already-disputed swap"
        if (msg.sender == swaps[swapID].maker) {
            swaps[swapID].disputeRaiser = DisputeRaiser.MAKER;
        } else if (msg.sender == swaps[swapID].taker) {
            swaps[swapID].disputeRaiser = DisputeRaiser.TAKER;
        } else {
            revert("e44"); //"e44": "Only swap maker or taker can call this function"
        }

        //Record the block number at which the dispute is raised
        disputes[swapID].disputeRaisedBlockNum = block.number;
        //Record the addresses of selected dispute agents
        disputes[swapID].disputeAgent0 = disputeAgent0;
        disputes[swapID].disputeAgent1 = disputeAgent1;
        disputes[swapID].disputeAgent2 = disputeAgent2;

        emit DisputeRaised(swapID, disputeAgent0, disputeAgent1, disputeAgent2);
    }

}
