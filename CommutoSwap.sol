// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

//import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.0/contracts/math/SafeMath.sol";
import "./libraries/AbstractERC20.sol";
import "./libraries/CommutoSwapOfferOpener.sol";
import "./libraries/CommutoSwapStorage.sol";
import "./libraries/CommutoSwapTypes.sol";
import "./libraries/SafeMath.sol";
import "./libraries/CommutoSwapPaymentReporter.sol";

//TODO: Fee percentage set by token holders
//TODO: Better code comments
contract CommutoSwap is CommutoSwapStorage {

    //Set the supported state of a settlement method
    function setSettlementMethodSupport(bytes calldata settlementMethod, bool support) public {
        require(msg.sender == owner, "e45"); //"e45": "Only owner can set settlement method support",
        bool foundSettlementMethod = false;
        for (uint i = 0; i < supportedSettlementMethods.length; i++) {
            if (sha256(supportedSettlementMethods[i]) == sha256(settlementMethod) && support == false) {
                foundSettlementMethod = true;
                delete supportedSettlementMethods[i];
                supportedSettlementMethods[i] = supportedSettlementMethods[supportedSettlementMethods.length - 1];
                supportedSettlementMethods.pop();
                break;
            }
            else if (sha256(supportedSettlementMethods[i]) == sha256(settlementMethod) && support == true) {
                foundSettlementMethod = true;
                break;
            }
        }
        if (foundSettlementMethod == false && support == true) {
            supportedSettlementMethods.push(settlementMethod);
        }
        settlementMethods[settlementMethod] = support;
    }

    //Get a copy of the array of supported settlement methods
    function getSupportedSettlementMethods() view public returns (bytes[] memory) {
        return supportedSettlementMethods;
    }

    //Set the supported state of a settlement method
    function setStablecoinSupport(address stablecoin, bool support) public {
        require(msg.sender == owner, "e49"); //"e49": "Only owner can set stablecoin support"
        bool foundStablecoin = false;
        for (uint i = 0; i < supportedStablecoins.length; i++) {
            if (supportedStablecoins[i] == stablecoin && support == false) {
                foundStablecoin = true;
                delete supportedStablecoins[i];
                supportedStablecoins[i] = supportedStablecoins[supportedStablecoins.length - 1];
                supportedStablecoins.pop();
                break;
            }
            else if (supportedStablecoins[i] == stablecoin && support == true) {
                foundStablecoin = true;
                break;
            }
        }
        if (foundStablecoin == false && support == true) {
            supportedStablecoins.push(stablecoin);
        }
        stablecoins[stablecoin] = support;
    }

    //Get a copy of the array of supported stablecoins
    function getSupportedStablecoins() view public returns (address[] memory) {
        return supportedStablecoins;
    }

    /*
    Set the active state of a dispute agent (True = active, shall resolve disputes, False = not active, shall not
    resolve disputes)
    */
    function setDisputeAgentActive(address disputeAgentAddress, bool setActive) public {
        require(msg.sender == owner, "e1"); //"e1": "Only contract owner can set dispute agent activity state"
        require(disputeAgentAddress != address(0), "e2"); //"e2": "Dispute agent address cannot be the zero address"
        bool foundDisputeAgent = false;
        //Search for dispute agent in list of active dispute agents
        for (uint i = 0; i < activeDisputeAgents.length; i++) {
            if (activeDisputeAgents[i] == disputeAgentAddress && setActive == false) {
                //Have found dispute agent and are setting them as not active
                foundDisputeAgent = true;
                delete activeDisputeAgents[i];
                activeDisputeAgents[i] = activeDisputeAgents[activeDisputeAgents.length - 1];
                activeDisputeAgents.pop();
                break;
            }
            else if (activeDisputeAgents[i] == disputeAgentAddress && setActive == true) {
                //Have found dispute agent and want to set them as active, but they already are active
                foundDisputeAgent = true;
                break;
            }
        }
        if (foundDisputeAgent == false && setActive == true) {
            //Didn't find them and are setting them as activeDisputeAgents
            activeDisputeAgents.push(disputeAgentAddress);
        }
        //Set status in map
        disputeAgents[disputeAgentAddress] = setActive;
    }

    //Get a copy of the array of active dispute agents
    function getActiveDisputeAgents() view public returns (address[] memory) {
        return activeDisputeAgents;
    }

    function getOffer(bytes16 offerID) view public returns (Offer memory) {
        return offers[offerID];
    }

    function getSwap(bytes16 swapID) view public returns (Swap memory) {
        return swaps[swapID];
    }

    constructor (address _serviceFeePool, address offerOpener, address offerEditor, address offerCanceler, address offerTaker, address swapFiller, address paymentReporter, address swapCloser) public CommutoSwapStorage(offerOpener, offerEditor, offerCanceler, offerTaker, swapFiller, paymentReporter, swapCloser) {
        owner = msg.sender;
        require(_serviceFeePool != address(0), "e0"); //"e0": "_serviceFeePool address cannot be zero"
        serviceFeePool = _serviceFeePool;
    }

    //Create a new swap offer
    function openOffer(bytes16 offerID, Offer memory newOffer) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapOfferOpener address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapOfferOpener.delegatecall(
            abi.encodeWithSignature("openOffer(bytes16,(bool,bool,address,bytes,address,uint256,uint256,uint256,uint8,bytes,bytes[],uint256))",
            offerID, newOffer)
        );
        require(success, string (data) );
    }

    //Edit the price and supported settlement methods of an open swap offer
    function editOffer(bytes16 offerID, Offer memory editedOffer, bool editPrice, bool editSettlementMethods) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapOfferEditor address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapOfferEditor.delegatecall(
            abi.encodeWithSignature("editOffer(bytes16,(bool,bool,address,bytes,address,uint256,uint256,uint256,uint8,bytes,bytes[],uint256),bool,bool)",
            offerID, editedOffer, editPrice, editSettlementMethods)
        );
        require(success, string (data) );
    }

    //Cancel open swap offer
    function cancelOffer(bytes16 offerID) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapOfferCanceler address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapOfferCanceler.delegatecall(
            abi.encodeWithSignature("cancelOffer(bytes16)",
            offerID)
        );
        require(success, string (data) );
    }

    //Take a swap offer
    function takeOffer(bytes16 offerID, Swap memory newSwap) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapOfferTaker address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapOfferTaker.delegatecall(
            abi.encodeWithSignature("takeOffer(bytes16,(bool,bool,address,bytes,address,bytes,address,uint256,uint256,uint256,uint256,uint256,uint8,bytes,bytes,uint256,bool,bool,bool,bool,uint8))",
            offerID, newSwap)
        );
        require(success, string (data) );
    }

    //TODO: More fillSwap tests
    //Fill swap (deposit takenSwapAmount of STBL) as maker and seller
    function fillSwap(bytes16 swapID) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapFiller address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapFiller.delegatecall(
            abi.encodeWithSignature("fillSwap(bytes16)",
            swapID)
        );
        require(success, string (data) );
    }

    //Report payment sent for swap
    function reportPaymentSent(bytes16 swapID) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapPaymentReporter address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapPaymentReporter.delegatecall(
            abi.encodeWithSignature("reportPaymentSent(bytes16)",
            swapID)
        );
        require(success, string (data) );
    }

    //Report payment received for swap
    function reportPaymentReceived(bytes16 swapID) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapPaymentReporter address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapPaymentReporter.delegatecall(
            abi.encodeWithSignature("reportPaymentReceived(bytes16)",
            swapID)
        );
        require(success, string (data) );
    }

    //Close swap and receive STBL from escrow
    function closeSwap(bytes16 swapID) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapCloser address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapCloser.delegatecall(
            abi.encodeWithSignature("closeSwap(bytes16)",
            swapID)
        );
        require(success, string (data) );
    }

    //Raise a dispute for a swap
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

    //Propose a resolution to a disputed swap
    function proposeResolution(bytes16 swapID, uint256 makerPayout, uint256 takerPayout, uint256 confiscationPayout) public {
        require(swaps[swapID].disputeRaiser != DisputeRaiser.NONE, "e54"); //"e54": "Swap doesn't exist or isn't disputed"
        uint256 serviceFeeAmountUpperBound = SafeMath.div(swaps[swapID].amountUpperBound, 100); //The amount the maker paid upon swap creation to pay the service fee
        uint256 unspentServiceFee = SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount); //The remaining amount owed to the maker after subtracting service fee
        uint256 totalSecurityDeposit = SafeMath.mul(swaps[swapID].securityDepositAmount, 2); //The sum of the maker's and taker's security deposits
        uint256 totalWithSpentServiceFees = SafeMath.add(swaps[swapID].takenSwapAmount, SafeMath.add(totalSecurityDeposit, unspentServiceFee)); //The total amount of STBL locked up by the maker and taker
        uint256 totalWithoutSpentServiceFees = SafeMath.sub(totalWithSpentServiceFees, SafeMath.mul(2, swaps[swapID].serviceFeeAmount)); //Total minus spent service fees
        uint256 swapperPayout = SafeMath.add(makerPayout, takerPayout); //Total payout to maker and taker
        uint256 totalPayout = SafeMath.add(swapperPayout, confiscationPayout); //Total payout, including that to the fee pool
        require(totalPayout == totalWithoutSpentServiceFees, "e56");

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

    function reactToResolutionProposal(bytes16 swapID, DisputeReaction reaction) public {
        require(reaction != DisputeReaction.NO_REACTION, "e58"); //"e58": "Can't react with no reaction"
        if (msg.sender == swaps[swapID].maker) {
            require(disputes[swapID].makerReaction == DisputeReaction.NO_REACTION, "e59"); //"e59": "Maker can't react to resolution proposal more than once"
            disputes[swapID].makerReaction = reaction;
        } else if (msg.sender == swaps[swapID].taker) {
            require(disputes[swapID].takerReaction == DisputeReaction.NO_REACTION, "e60"); //"e60": "Taker can't react to resolution proposal more than once"
            disputes[swapID].takerReaction = reaction;
        } else {
            revert("e57");
        }
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
        }
        require(foundMatchingResolutionProposals, "e61"); //"e61": "Two matching resolutions must be proposed before reaction is allowed"
    }

}