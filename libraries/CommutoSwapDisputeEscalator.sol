// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

/*
Contains the escalateDispute method, to which CommutoSwap delegates escalateDispute calls to escalate disputed swaps.
This contract holds nothing in its own storage, its method is intended only for use via delegatecall, so reactions
cannot be submitted by calling CommutoSwapDisputeEscalator directly.
*/
contract CommutoSwapDisputeEscalator is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Escalate a disputed swap
    function escalateDispute(bytes16 swapID, EscalationReason reason) public {
        require(msg.sender == swaps[swapID].maker || msg.sender == swaps[swapID].taker, "e75"); //"e75": "Only maker or taker can escalate disputed swap"
        require(disputes[swapID].state != DisputeState.ESCALATED, "e78"); //"e78": "Cannot escalate dispute if dispute has already been escalated"
        if (reason == EscalationReason.NO_DISPUTE_AGENT_AGREEMENT) {
            require(block.number > SafeMath.add(minimumDisputePeriod, disputes[swapID].disputeRaisedBlockNum), "e71"); //"e71": "More blocks must be mined before swap can be escalated"
            /*
            Check if at least two dispute agents have submitted matching resolution proposals
            See reactToResolutionProposal() to understand logic behind this code
            */
            bool foundMatchingResolutionProposals = false;
            if (disputes[swapID].hasDA0Proposed && disputes[swapID].hasDA1Proposed) {
                foundMatchingResolutionProposals = (
                (disputes[swapID].dA0MakerPayout == disputes[swapID].dA1MakerPayout) &&
                (disputes[swapID].dA0TakerPayout == disputes[swapID].dA1TakerPayout) &&
                (disputes[swapID].dA0ConfiscationPayout == disputes[swapID].dA1ConfiscationPayout)
                );
            }
            if ((disputes[swapID].hasDA1Proposed && disputes[swapID].hasDA2Proposed) && !foundMatchingResolutionProposals) {
                foundMatchingResolutionProposals = (
                (disputes[swapID].dA1MakerPayout == disputes[swapID].dA2MakerPayout) &&
                (disputes[swapID].dA1TakerPayout == disputes[swapID].dA2TakerPayout) &&
                (disputes[swapID].dA1ConfiscationPayout == disputes[swapID].dA2ConfiscationPayout)
                );
            }
            if ((disputes[swapID].hasDA0Proposed && disputes[swapID].hasDA2Proposed) && !foundMatchingResolutionProposals) {
                foundMatchingResolutionProposals = (
                (disputes[swapID].dA0MakerPayout == disputes[swapID].dA2MakerPayout) &&
                (disputes[swapID].dA0TakerPayout == disputes[swapID].dA2TakerPayout) &&
                (disputes[swapID].dA0ConfiscationPayout == disputes[swapID].dA2ConfiscationPayout)
                );
            }
            require(!foundMatchingResolutionProposals, "e73"); //"e73": "Dispute can't be escalated for lack of dispute agent response if dispute agents have agreed on resolution proposal"
        } else if (reason == EscalationReason.NO_COUNTERPARTY_REACTION) {
            require(block.number > SafeMath.add(minimumDisputePeriod, disputes[swapID].disputeRaisedBlockNum), "e71"); //"e71": "More blocks must be mined before swap can be escalated"
            if (msg.sender == swaps[swapID].maker) {
                require(disputes[swapID].makerReaction != DisputeReaction.NO_REACTION, "e76"); //"e76": "Dispute cannot be escalated for lack of counterparty reaction if caller has not reacted"
                require(disputes[swapID].takerReaction == DisputeReaction.NO_REACTION, "e74"); //"e74": "Dispute cannot be escalated for lack of counterparty reaction if counterparty has reacted"
            } else if (msg.sender == swaps[swapID].taker) {
                require(disputes[swapID].takerReaction != DisputeReaction.NO_REACTION, "e76"); //"e76": "Dispute cannot be escalated for lack of counterparty reaction if caller has not reacted"
                require(disputes[swapID].makerReaction == DisputeReaction.NO_REACTION, "e74"); //"e74": "Dispute cannot be escalated for lack of counterparty reaction if counterparty has reacted"
            } else {
                revert("e75"); //"e75": "Only maker or taker can escalate disputed swap"
            }
        } else {
            require(disputes[swapID].makerReaction == DisputeReaction.REJECTED || disputes[swapID].takerReaction == DisputeReaction.REJECTED, "e72"); //"e72": "Resolution proposal must be rejected to escalate dispute because of rejection"
        }

        //Find proper stablecoin contract
        ERC20 token = ERC20(swaps[swapID].stablecoin);
        //TODO: Service fee calculated here
        uint256 serviceFeeAmountUpperBound = SafeMath.mul(swaps[swapID].serviceFeeRate, SafeMath.div(swaps[swapID].amountUpperBound, 10000)); //The amount the maker paid upon swap creation to pay the service fee
        uint256 unspentServiceFee = SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount); //The remaining amount owed to the maker after subtracting actual service fee
        uint256 totalSecurityDeposit = SafeMath.mul(swaps[swapID].securityDepositAmount, 2); //The sum of the maker's and taker's security deposits
        uint256 totalWithoutSpentServiceFees = 0; //The total amount of STBL locked up by the maker and taker, excluding service fees
        if (swaps[swapID].requiresFill == true) {
            /*
            See comment in proposeResolution() to understand the logic behind this code
            */
            totalWithoutSpentServiceFees = SafeMath.add(totalSecurityDeposit, unspentServiceFee);
        } else {
            totalWithoutSpentServiceFees = SafeMath.add(swaps[swapID].takenSwapAmount, SafeMath.add(totalSecurityDeposit, unspentServiceFee));
        }
        disputes[swapID].state = DisputeState.ESCALATED;
        disputes[swapID].totalWithoutSpentServiceFees = totalWithoutSpentServiceFees;

        emit DisputeEscalated(swapID, msg.sender, reason);

        require(token.transfer(primaryTimelock, SafeMath.mul(2, swaps[swapID].serviceFeeAmount)), "e42"); //"e42": "Service fee transfer failed"
    }
}
