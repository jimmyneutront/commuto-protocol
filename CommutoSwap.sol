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
import "./libraries/CommutoSwapResolutionProposalReactor.sol";

//TODO: Update documentation for governance
contract CommutoSwap is CommutoSwapStorage {

    //Transfer control of CommutoToken to a new timelock
    function changeTimelock(address newTimelock) public {
        require(msg.sender == timelock, "e79"); //"e79": "Only the current Timelock can call this function"
        emit TimelockChanged(timelock, newTimelock);
        timelock = newTimelock;
    }

    //Set the new service fee rate
    function setServiceFeeRate(uint256 newServiceFeeRate) public {
        require(msg.sender == timelock, "e79"); //"e79": "Only the current Timelock can call this function"
        serviceFeeRate = newServiceFeeRate;
        emit ServiceFeeRateChanged(newServiceFeeRate);
    }

    //Get the service fee rate
    function getServiceFeeRate() view public returns (uint256) {
        return serviceFeeRate;
    }

    //Set the new minimum dispute period
    function setMinimumDisputePeriod(uint256 newMinimumDisputePeriod) public {
        require(msg.sender == timelock, "e79"); //"e79": "Only the current Timelock can call this function"
        minimumDisputePeriod = newMinimumDisputePeriod;
        emit MinimumDisputePeriodChanged(newMinimumDisputePeriod);
    }

    //Get the minimum dispute period
    function getMinimumDisputePeriod() view public returns (uint256) {
        return minimumDisputePeriod;
    }

    //Set the supported state of a settlement method
    function setSettlementMethodSupport(bytes calldata settlementMethod, bool support) public {
        require(msg.sender == timelock, "e45"); //"e45": "Only timelock can set settlement method support",
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
        require(msg.sender == timelock, "e49"); //"e49": "Only timelock can set stablecoin support"
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
        require(msg.sender == timelock, "e1"); //"e1": "Only contract timelock can set dispute agent activity state"
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

    function getDispute(bytes16 swapID) view public returns (Dispute memory) {
        return disputes[swapID];
    }

    constructor (address[] memory contractAddresses) public CommutoSwapStorage(contractAddresses[1], contractAddresses[2], contractAddresses[3], contractAddresses[4], contractAddresses[5], contractAddresses[6], contractAddresses[7], contractAddresses[8], contractAddresses[9], contractAddresses[10], contractAddresses[11]) {
        timelock = msg.sender;
        require(contractAddresses[0] != address(0), "e0"); //"e0": "_serviceFeePool address cannot be zero"
        serviceFeePool = contractAddresses[0];
    }

    //Create a new swap offer
    function openOffer(bytes16 offerID, Offer memory newOffer) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapOfferOpener address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapOfferOpener.delegatecall(
            abi.encodeWithSignature("openOffer(bytes16,(bool,bool,address,bytes,address,uint256,uint256,uint256,uint256,uint8,bytes,bytes[],uint256))",
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
            abi.encodeWithSignature("editOffer(bytes16,(bool,bool,address,bytes,address,uint256,uint256,uint256,uint256,uint8,bytes,bytes[],uint256),bool,bool)",
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
            abi.encodeWithSignature("takeOffer(bytes16,(bool,bool,address,bytes,address,bytes,address,uint256,uint256,uint256,uint256,uint256,uint256,uint8,bytes,bytes,uint256,bool,bool,bool,bool,uint8))",
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
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapDisputeRaiser address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapDisputeRaiser.delegatecall(
            abi.encodeWithSignature("raiseDispute(bytes16,address,address,address)",
            swapID, disputeAgent0, disputeAgent1, disputeAgent2)
        );
        require(success, string (data) );
    }

    //Propose a resolution to a disputed swap
    function proposeResolution(bytes16 swapID, uint256 makerPayout, uint256 takerPayout, uint256 confiscationPayout) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapDisputeRaiser address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapResolutionProposer.delegatecall(
            abi.encodeWithSignature("proposeResolution(bytes16,uint256,uint256,uint256)",
            swapID, makerPayout, takerPayout, confiscationPayout)
        );
        require(success, string (data) );
    }

    //React to the dispute agents' resolution proposals
    function reactToResolutionProposal(bytes16 swapID, DisputeReaction reaction) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapResolutionProposalReactor and
        CommutoSwapDisputeEscalator address are immutable and set when CommutoSwap is deployed, and therefore calls
        cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapResolutionProposalReactor.delegatecall(
            abi.encodeWithSignature("reactToResolutionProposal(bytes16,uint8)",
            swapID, reaction)
        );
        require(success, string (data) );

        //Immediately mark dispute as escalated if reaction is rejection
        if (reaction == DisputeReaction.REJECTED) {
            /*
            Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
            contract size limitations, and also safe since the CommutoSwapDisputeEscalator address is immutable and
            set when CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
            */
            (bool success, bytes memory data) = commutoSwapDisputeEscalator.delegatecall(
                abi.encodeWithSignature("escalateDispute(bytes16,uint8)",
                swapID, EscalationReason.REJECTION)
            );
            require(success, string (data) );
        }

    }

    //Close a swap that has been disputed
    function closeDisputedSwap(bytes16 swapID) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapCloser address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapCloser.delegatecall(
            abi.encodeWithSignature("closeDisputedSwap(bytes16)",
            swapID)
        );
        require(success, string (data) );
    }

    //Escalate a disputed swap
    function escalateDispute(bytes16 swapID, EscalationReason reason) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapDisputeEscalator address is immutable and
        set when CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapDisputeEscalator.delegatecall(
            abi.encodeWithSignature("escalateDispute(bytes16,uint8)",
            swapID, reason)
        );
        require(success, string (data) );
    }

    //Close a swap that has been escalated, using an approved governance proposal executed by the timelock
    function closeEscalatedSwap(bytes16 swapID, uint256 makerPayout, uint256 takerPayout, uint256 confiscationPayout) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also safe since the CommutoSwapCloser address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapCloser.delegatecall(
            abi.encodeWithSignature("closeEscalatedSwap(bytes16,uint256,uint256,uint256)",
            swapID, makerPayout, takerPayout, confiscationPayout)
        );
        require(success, string (data) );
    }

}