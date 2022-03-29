// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import "./AbstractERC20.sol";
import "./CommutoSwapStorage.sol";
import "./CommutoSwapTypes.sol";
import "./SafeMath.sol";

/*
Contains the proposeResolution method, to which CommutoSwap delegates proposeResolution calls to propose resolutions.
This contract holds nothing in its own storage; its method is intended only for use via delegatecall, so resolutions
cannot be proposed by calling CommutoSwapResolutionProposer directly.
*/
contract CommutoSwapResolutionProposer is CommutoSwapStorage{

    constructor() CommutoSwapStorage(address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0), address(0)) public {}

    //Propose a resolution to a disputed swap
    function proposeResolution(bytes16 swapID, uint256 makerPayout, uint256 takerPayout, uint256 confiscationPayout) public {
        require(swaps[swapID].disputeRaiser != DisputeRaiser.NONE, "e54"); //"e54": "Swap doesn't exist or isn't disputed"
        require(disputes[swapID].state != DisputeState.ESCALATED, "e68"); //"e68": "A resolution cannot be proposed for an escalated swap"
        //TODO: Service fee calculated here
        uint256 serviceFeeAmountUpperBound = SafeMath.mul(swaps[swapID].serviceFeeRate, SafeMath.div(swaps[swapID].amountUpperBound, 10000)); //The amount the maker paid upon swap creation to pay the service fee
        uint256 unspentServiceFee = SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount); //The remaining amount owed to the maker after subtracting actual service fee
        uint256 totalSecurityDeposit = SafeMath.mul(swaps[swapID].securityDepositAmount, 2); //The sum of the maker's and taker's security deposits
        uint256 totalWithoutSpentServiceFees = 0; //The total amount of STBL locked up by the maker and taker, excluding service fees
        if (swaps[swapID].requiresFill == true) {
            /*
            If the swap is a maker-as-seller swap and the maker hasn't filled the swap yet, then dispute agents
            shouldn't be able to propose a resolution with a total payout greater than the swap amount, since that would
            mean CommutoSwap is paying out more stablecoin than it is taking in.
            If requiresFill is true for a swap, then it is a maker-as-seller swap that hasn't been filled yet.
            If requiresFill is false, then either it is a maker-as-seller swap that has been filled, or it isn't a
            maker-as-seller swap. In either case, if requiresFill is false, the taken swap amount of stablecoin has been
            locked up in CommutoSwap, so we include it in the total pay in amount. Accordingly, we don't include it if
            requiresFill is true.
            */
            totalWithoutSpentServiceFees = SafeMath.add(totalSecurityDeposit, unspentServiceFee);
        } else {
            totalWithoutSpentServiceFees = SafeMath.add(swaps[swapID].takenSwapAmount, SafeMath.add(totalSecurityDeposit, unspentServiceFee));
        }
        uint256 swapperPayout = SafeMath.add(makerPayout, takerPayout); //Total payout to maker and taker
        uint256 totalPayout = SafeMath.add(swapperPayout, confiscationPayout); //Total payout, including that to the fee pool
        require(totalPayout == totalWithoutSpentServiceFees, "e56"); //"e56": "Total payout amount must equal total amount paid in minus service fees"
        require((disputes[swapID].makerReaction == DisputeReaction.NO_REACTION) && (disputes[swapID].takerReaction == DisputeReaction.NO_REACTION), "e62"); //"e62": "A resolution proposal cannot be submitted if the maker or taker has already reacted"

        if (msg.sender == disputes[swapID].disputeAgent0) {
            disputes[swapID].dA0MakerPayout = makerPayout;
            disputes[swapID].dA0TakerPayout = takerPayout;
            disputes[swapID].dA0ConfiscationPayout = confiscationPayout;
            disputes[swapID].hasDA0Proposed = true;
        } else if (msg.sender == disputes[swapID].disputeAgent1) {
            disputes[swapID].dA1MakerPayout = makerPayout;
            disputes[swapID].dA1TakerPayout = takerPayout;
            disputes[swapID].hasDA1Proposed = true;
            disputes[swapID].dA1ConfiscationPayout = confiscationPayout;
        } else if (msg.sender == disputes[swapID].disputeAgent2) {
            disputes[swapID].dA2MakerPayout = makerPayout;
            disputes[swapID].dA2TakerPayout = takerPayout;
            disputes[swapID].hasDA2Proposed = true;
            disputes[swapID].dA2ConfiscationPayout = confiscationPayout;
        } else {
            revert("e55"); //"e55": "Only a dispute agent selected for the swap can propose a resolution"
        }

        emit ResolutionProposed(swapID, msg.sender);

    }

}
