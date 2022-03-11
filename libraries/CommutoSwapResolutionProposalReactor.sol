// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

/*
Contains the reactToResolutionProposal method, to which CommutoSwap delegates reactToResolutionProposal calls to react
to resolution proposals. This contract holds nothing in its own storage, its method is intended only for use via
delegatecall, so reactions cannot be submitted by calling CommutoSwapResolutionProposalReactor directly.
*/
contract CommutoSwapResolutionProposalReactor is CommutoSwapStorage {

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //React to the dispute agents' resolution proposals
    function reactToResolutionProposal(bytes16 swapID, DisputeReaction reaction) public {
        require(reaction != DisputeReaction.NO_REACTION, "e58"); //"e58": "Can't react with no reaction"
        require(disputes[swapID].state != DisputeState.ESCALATED, "e69"); //"e69": "A reaction cannot be submitted for an escalated swap"
        if (msg.sender == swaps[swapID].maker) {
            require(disputes[swapID].makerReaction == DisputeReaction.NO_REACTION, "e59"); //"e59": "Maker can't react to resolution proposal more than once"
            disputes[swapID].makerReaction = reaction;
        } else if (msg.sender == swaps[swapID].taker) {
            require(disputes[swapID].takerReaction == DisputeReaction.NO_REACTION, "e60"); //"e60": "Taker can't react to resolution proposal more than once"
            disputes[swapID].takerReaction = reaction;
        } else {
            revert("e57"); //"e57": "Only swap maker or taker can react to resolution proposal"
        }

        //Only search for matching resolution proposals if we haven't found a matching pair yet
        if (disputes[swapID].matchingProposals == MatchingProposalPair.NO_MATCH) {
            //Check if at least two dispute agents have submitted matching resolution proposals
            bool foundMatchingResolutionProposals = false;
            /*
            Check if dispute agents 0 and 1 have submitted proposals. If they have, check if their proposals match.
            */
            if (disputes[swapID].hasDA0Proposed && disputes[swapID].hasDA1Proposed) {
                foundMatchingResolutionProposals = (
                (disputes[swapID].dA0MakerPayout == disputes[swapID].dA1MakerPayout) &&
                (disputes[swapID].dA0TakerPayout == disputes[swapID].dA1TakerPayout) &&
                (disputes[swapID].dA0ConfiscationPayout == disputes[swapID].dA1ConfiscationPayout)
                );
                if (foundMatchingResolutionProposals == true) {
                    disputes[swapID].matchingProposals = MatchingProposalPair.ZERO_AND_ONE;
                }
            }
            /*
            If dispute agents 0 and 1 haven't submitted matching proposals (which also includes the possibility that they
            haven't submitted proposals at all) check if dispute agents 1 and 2 have submitted proposals. If they have,
            check if their proposals match.
            */
            if ((disputes[swapID].hasDA1Proposed && disputes[swapID].hasDA2Proposed) && !foundMatchingResolutionProposals) {
                foundMatchingResolutionProposals = (
                (disputes[swapID].dA1MakerPayout == disputes[swapID].dA2MakerPayout) &&
                (disputes[swapID].dA1TakerPayout == disputes[swapID].dA2TakerPayout) &&
                (disputes[swapID].dA1ConfiscationPayout == disputes[swapID].dA2ConfiscationPayout)
                );
                if (foundMatchingResolutionProposals == true) {
                    disputes[swapID].matchingProposals = MatchingProposalPair.ONE_AND_TWO;
                }
            }
            /*
            At this point, proposals (if any) submitted by dispute agents zero and one don't match, and proposals (if any)
            submitted by dispute agents one and two don't match, so check if dispute agents zero and two have submitted
            proposals. If they have, check if their proposals match.
            */
            if ((disputes[swapID].hasDA0Proposed && disputes[swapID].hasDA2Proposed) && !foundMatchingResolutionProposals) {
                foundMatchingResolutionProposals = (
                (disputes[swapID].dA0MakerPayout == disputes[swapID].dA2MakerPayout) &&
                (disputes[swapID].dA0TakerPayout == disputes[swapID].dA2TakerPayout) &&
                (disputes[swapID].dA0ConfiscationPayout == disputes[swapID].dA2ConfiscationPayout)
                );
                if (foundMatchingResolutionProposals == true) {
                    disputes[swapID].matchingProposals = MatchingProposalPair.ZERO_AND_TWO;
                }
            }
            require(foundMatchingResolutionProposals, "e61"); //"e61": "Two matching resolutions must be proposed before reaction is allowed"
        }

        //TODO: Delegate call to dispute escalator here

        emit ReactionSubmitted(swapID, msg.sender, reaction);
    }

}
