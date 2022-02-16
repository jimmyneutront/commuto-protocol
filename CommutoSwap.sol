// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

//import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.0/contracts/math/SafeMath.sol";
import "./libraries/AbstractERC20.sol";
import "./libraries/CommutoSwapOfferOpener.sol";
import "./libraries/CommutoSwapStorage.sol";
import "./libraries/CommutoSwapTypes.sol";
import "./libraries/SafeMath.sol";

//TODO: Deal with contract size limitation
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

    function getOffer(bytes16 offerID) view public returns (Offer memory) {
        return offers[offerID];
    }

    function getSwap(bytes16 swapID) view public returns (Swap memory) {
        return swaps[swapID];
    }

    constructor (address _serviceFeePool, address offerOpener, address offerEditor, address offerCanceler, address offerTaker) public CommutoSwapStorage(offerOpener, offerEditor, offerCanceler, offerTaker) {
        owner = msg.sender;
        require(_serviceFeePool != address(0), "e0"); //"e0": "_serviceFeePool address cannot be zero"
        serviceFeePool = _serviceFeePool;
    }

    //Create a new swap offer by delegating to CommutoSwapOfferOpener
    function openOffer(bytes16 offerID, Offer memory newOffer) public {
        /*
        Slither throws a high severity warning about the use of delegatecall. In this case it is necessary due to
        contract size limitations, and also save since the CommutoSwapOfferOpener address is immutable and set when
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
        contract size limitations, and also save since the CommutoSwapOfferEditor address is immutable and set when
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
        contract size limitations, and also save since the CommutoSwapOfferCanceler address is immutable and set when
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
        contract size limitations, and also save since the CommutoSwapOfferEditor address is immutable and set when
        CommutoSwap is deployed, and therefore the call cannot be delegated to a malicious contract.
        */
        (bool success, bytes memory data) = commutoSwapOfferTaker.delegatecall(
            abi.encodeWithSignature("takeOffer(bytes16,(bool,bool,address,bytes,address,bytes,address,uint256,uint256,uint256,uint256,uint256,uint8,bytes,bytes,uint256,bool,bool,bool,bool))",
            offerID, newSwap)
        );
        require(success, string (data) );
    }

    //TODO: More fillSwap tests
    //Fill swap (deposit takenSwapAmount of STBL) as maker and seller
    function fillSwap(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(swaps[swapID].requiresFill && swaps[swapID].direction == SwapDirection.SELL, "e18"); //"e18": "Swap does not require filling"
        require(swaps[swapID].maker == msg.sender, "e47"); //"e47": "Only maker and seller can fill swap"

        //Update swap state
        swaps[swapID].requiresFill = false;
        emit SwapFilled(swapID);

        //Find proper stablecoin contract
        ERC20 token = ERC20(swaps[swapID].stablecoin);

        //Lock taken swap amount in escrow
        require(swaps[swapID].takenSwapAmount <= token.allowance(msg.sender, address(this)), "e13"); //"e13": "Token allowance must be >= required amount"
        require(token.transferFrom(msg.sender, address(this), swaps[swapID].takenSwapAmount), "e14"); //"e14": "Token transfer to Commuto Protocol failed"
    }

    //Report payment sent for swap
    function reportPaymentSent(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(!swaps[swapID].requiresFill, "e48"); //"e48": "The swap must be filled before payment is sent"
        require(!swaps[swapID].isPaymentSent, "e34"); //"e34": "Payment sending has already been reported for swap with specified id"
        if(swaps[swapID].direction == SwapDirection.BUY) {
            require(swaps[swapID].maker == msg.sender, "e35"); //"e35": "Payment sending can only be reported by buyer"
        } else if (swaps[swapID].direction == SwapDirection.SELL) {
            require(swaps[swapID].taker == msg.sender, "e35"); //"e35": "Payment sending can only be reported by buyer"
        } else {
            revert("e36"); //"e36": "Swap has invalid direction"
        }

        //Mark payment sent and notify
        swaps[swapID].isPaymentSent = true;
        emit PaymentSent(swapID);
    }

    //Report payment received for swap
    function reportPaymentReceived(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(swaps[swapID].isPaymentSent, "e37"); //"e37": "Payment sending has not been reported for swap with specified id"
        require(!swaps[swapID].isPaymentReceived, "e38"); //"e38": "Payment receiving has already been reported for swap with specified id"
        if(swaps[swapID].direction == SwapDirection.BUY) {
            require(swaps[swapID].taker == msg.sender, "e39"); //"e39": "Payment receiving can only be reported by seller"
        } else if (swaps[swapID].direction == SwapDirection.SELL) {
            require(swaps[swapID].maker == msg.sender, "e39"); //"e39": "Payment receiving can only be reported by seller"
        } else {
            revert("e36"); //"e36": "Swap has invalid direction"
        }

        //Mark payment received and notify
        swaps[swapID].isPaymentReceived = true;
        emit PaymentReceived(swapID);
    }

    //Close swap and receive STBL from escrow
    function closeSwap(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
        require(swaps[swapID].isPaymentReceived, "e40"); //"e40": "Payment receiving has not been reported for swap with specified id"

        //Find proper stablecoin contract
        ERC20 token = ERC20(swaps[swapID].stablecoin);

        uint256 returnAmount;

        //If caller is buyer and taker, return security deposit and swap amount, and send service fee to pool
        if(swaps[swapID].direction == SwapDirection.SELL && swaps[swapID].taker == msg.sender) {
            require(!swaps[swapID].hasBuyerClosed, "e41"); //"e41": "Buyer has already closed swap"
            returnAmount = SafeMath.add(swaps[swapID].securityDepositAmount, swaps[swapID].takenSwapAmount);
            swaps[swapID].hasBuyerClosed = true;
            emit BuyerClosed(swapID);
            require(token.transfer(swaps[swapID].taker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        }
        //If caller is buyer and maker, return security deposit, swap amount, and serviceFeeUpperBound - serviceFeeAmount, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.BUY && swaps[swapID].maker == msg.sender) {
            require(!swaps[swapID].hasBuyerClosed, "e41"); //"e41": "Buyer has already closed swap"
            uint256 serviceFeeAmountUpperBound = SafeMath.div(swaps[swapID].amountUpperBound, 100);
            returnAmount = SafeMath.add(SafeMath.add(swaps[swapID].securityDepositAmount, swaps[swapID].takenSwapAmount), SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount));
            swaps[swapID].hasBuyerClosed = true;
            emit BuyerClosed(swapID);
            require(token.transfer(swaps[swapID].maker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        }
        //If caller is seller and taker, return security deposit, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.BUY && swaps[swapID].taker == msg.sender) {
            require(!swaps[swapID].hasSellerClosed, "e43"); //"e43": "Seller has already closed swap"
            returnAmount = swaps[swapID].securityDepositAmount;
            swaps[swapID].hasSellerClosed = true;
            emit SellerClosed(swapID);
            require(token.transfer(swaps[swapID].taker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        }
        //If caller is seller and maker, return security deposit and serviceFeeUpperBound - serviceFeeAmount, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.SELL && swaps[swapID].maker == msg.sender) {
            require(!swaps[swapID].hasSellerClosed, "e43"); //"e43": "Seller has already closed swap"
            uint256 serviceFeeAmountUpperBound = SafeMath.div(swaps[swapID].amountUpperBound, 100);
            returnAmount = SafeMath.add(swaps[swapID].securityDepositAmount, SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount));
            swaps[swapID].hasSellerClosed = true;
            emit SellerClosed(swapID);
            require(token.transfer(swaps[swapID].maker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        } else {
            revert("e44"); //"e44": "Only swap maker or taker can call this function"
        }
    }
}