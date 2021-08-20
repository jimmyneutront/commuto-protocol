// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.0/contracts/math/SafeMath.sol";

//Abstract ERC20 contract
abstract contract ERC20 {
  uint public totalSupply;

  event Transfer(address indexed from, address indexed to, uint value);
  event Approval(address indexed owner, address indexed spender, uint value);

  function balanceOf(address who) public view virtual returns (uint);
  function allowance(address owner, address spender) public view virtual returns (uint);

  function transfer(address to, uint value) public virtual returns (bool ok);
  function transferFrom(address from, address to, uint value) public virtual returns (bool ok);
  function approve(address spender, uint value) public virtual returns (bool ok);
}

//TODO: Better code comments
contract Commuto_Swap {
    
    address public owner;
    address public serviceFeePool;
    //TODO: Deal with decimal point precision differences between stablecoins
    address public daiAddress; //The address of a ERC20 contract to represent DAI
    address public usdcAddress; //The address of a ERC20 contract to represent USDC
    address public busdAddress; //The address of a ERC20 contract to represent BUSD
    address public usdtAddress; //The address of a ERC20 contract to represent USDT
    
    //The current version of the Commuto Protocol
    uint256 public protocolVersion = 0;
    
    enum SwapDirection  {
        BUY, //Maker has FIAT, wants STBL
        SELL //Maker has STBL, wants FIAT
    }
    
    //The stablecoin to be swapped
    enum StablecoinType {
        DAI,
        USDC,
        BUSD,
        USDT
    }
    
    //The payment method with which the buyer will send FIAT and the seller will receive FIAT
    enum PaymentMethod {
        MPESA,
        WECHAT,
        NEQUI,
        ZELLE,
        SEPA_INSTANT
    }
    
    struct Offer {
        bool isCreated;
        bool isTaken;
        address maker;
        bytes interfaceAddress;
        StablecoinType stablecoinType;
        uint256 amountLowerBound;
        uint256 amountUpperBound;
        uint256 securityDepositAmount;
        SwapDirection direction;
        bytes price;
        PaymentMethod paymentMethod;
        uint256 protocolVersion;
        bytes32 extraData;
    }

    struct Swap {
        bool isCreated;
        address maker;
        bytes makerInterfaceAddress;
        address taker;
        bytes takerInterfaceAddress;
        StablecoinType stablecoinType;
        uint256 amountLowerBound;
        uint256 amountUpperBound;
        uint256 securityDepositAmount;
        uint256 takenSwapAmount;
        uint256 serviceFeeAmount;
        SwapDirection direction;
        bytes price;
        PaymentMethod paymentMethod;
        uint256 protocolVersion;
        bytes32 makerExtraData;
        bytes32 takerExtraData;
        bool isPaymentSent;
        bool isPaymentReceived;
        bool hasBuyerClosed;
        bool hasSellerClosed;
    }
    
    event OfferOpened(bytes16 offerID);
    event OfferCanceled(bytes16 offerID);
    event OfferTaken(bytes16 offerID);
    event PaymentSent(bytes16 swapID);
    event PaymentReceived(bytes16 swapID);
    event BuyerClosed(bytes16 swapID);
    event SellerClosed(bytes16 swapID);
    
    mapping (bytes16 => Offer) private offers;
    mapping (bytes16 => Swap) private swaps;
    
    constructor (address _serviceFeePool,
                 address _daiAddress,
                 address _usdcAddress,
                 address _busdAddress,
                 address _usdtAddress) public {
        owner = msg.sender;
        serviceFeePool = _serviceFeePool;
        daiAddress = _daiAddress;
        usdcAddress = _usdcAddress;
        busdAddress = _busdAddress;
        usdtAddress = _usdtAddress;
    }

    //Create a new swap offer
    function openOffer(bytes16 offerID, Offer memory newOffer) public {
        //Validate arguments
        require(offers[offerID].isCreated == false, "An offer with the specified id already exists");
        require(newOffer.amountLowerBound > 0, "The minimum swap amount must be greater than zero");
        require(newOffer.amountUpperBound >= newOffer.amountLowerBound, "The maximum swap amount must be >= the minimum swap amount");
        require(SafeMath.mul(newOffer.securityDepositAmount, 10) >= newOffer.amountLowerBound, "The security deposit must be at least 10% of the minimum swap amount");
        uint256 serviceFeeAmountLowerBound = SafeMath.div(newOffer.amountLowerBound, 100);
        require(serviceFeeAmountLowerBound > 0, "Service fee amount must be greater than zero");
        require(newOffer.protocolVersion >= protocolVersion, "Offers can only be created for the most recent protocol version");
        
        //Find proper stablecoin contract
        ERC20 token;
        
        if(newOffer.stablecoinType == StablecoinType.DAI) {
            token = ERC20(daiAddress);
        } else if (newOffer.stablecoinType == StablecoinType.USDC) {
            token = ERC20(usdcAddress);
        } else if (newOffer.stablecoinType == StablecoinType.BUSD) {
            token = ERC20(busdAddress);
        } else if (newOffer.stablecoinType == StablecoinType.USDT) {
            token = ERC20(usdtAddress);
        } else {
            revert("You must specify a supported stablecoin");
        }

        //Calculate required total amount
        uint256 serviceFeeAmountUpperBound = SafeMath.div(newOffer.amountUpperBound, 100);
        uint256 totalAmount;
        if(newOffer.direction == SwapDirection.SELL) {
            totalAmount = SafeMath.add(SafeMath.add(newOffer.amountUpperBound, newOffer.securityDepositAmount), serviceFeeAmountUpperBound);
        } else if (newOffer.direction == SwapDirection.BUY) {
            totalAmount = SafeMath.add(newOffer.securityDepositAmount, serviceFeeAmountUpperBound);
        } else {
            revert("You must specify a supported direction");
        }
        //Lock required total amount in escrow
        require(totalAmount <= token.allowance(msg.sender, address(this)), "Token allowance must be >= required amount");
        require(token.transferFrom(msg.sender, address(this), totalAmount), "Token transfer to Commuto Protocol failed");

        //Finish and notify of offer creation
        newOffer.isCreated = true;
        newOffer.isTaken = false;
        newOffer.maker = msg.sender;
        offers[offerID] = newOffer;
        emit OfferOpened(offerID);
    }

    //Cancel open swap offer
    function cancelOffer(bytes16 offerID) public {
        //Validate arguments
        require(offers[offerID].isCreated, "An offer with the specified id does not exist");
        require(offers[offerID].isTaken == false, "Offer is taken and cannot be canceled");
        require(offers[offerID].maker == msg.sender, "Offers can only be canceled by offer maker");

        //Find proper stablecoin contract
        ERC20 token;

        if(offers[offerID].stablecoinType == StablecoinType.DAI) {
            token = ERC20(daiAddress);
        } else if (offers[offerID].stablecoinType == StablecoinType.USDC) {
            token = ERC20(usdcAddress);
        } else if (offers[offerID].stablecoinType == StablecoinType.BUSD) {
            token = ERC20(busdAddress);
        } else if (offers[offerID].stablecoinType == StablecoinType.USDT) {
            token = ERC20(usdtAddress);
        } else {
            revert("You must specify a supported stablecoin");
        }

        //Calculate total amount in escrow
        uint256 serviceFeeAmountUpperBound = SafeMath.div(offers[offerID].amountUpperBound, 100);
        uint256 totalAmount;
        if(offers[offerID].direction == SwapDirection.SELL) {
            totalAmount = SafeMath.add(SafeMath.add(offers[offerID].amountUpperBound, offers[offerID].securityDepositAmount), serviceFeeAmountUpperBound);
        } else if (offers[offerID].direction == SwapDirection.BUY) {
            totalAmount = SafeMath.add(offers[offerID].securityDepositAmount, serviceFeeAmountUpperBound);
        } else {
            revert("Offer has invalid direction");
        }

        //Delete offer, refund STBL and notify
        delete offers[offerID];
        require(token.transfer(offers[offerID].maker, totalAmount), "Token transfer failed");
        emit OfferCanceled(offerID);
    }

    //Take a swap offer
    function takeOffer(bytes16 offerID, Swap memory newSwap) public {
        //Validate arguments
        require(offers[offerID].isCreated, "An offer with the specified id does not exist");
        require(swaps[offerID].isCreated == false, "The offer with the specified id has already been taken");
        require(offers[offerID].maker == newSwap.maker, "Maker addresses must match");
        require(keccak256(offers[offerID].interfaceAddress) == keccak256(newSwap.makerInterfaceAddress), "Maker interface addresses must match");
        require(offers[offerID].stablecoinType == newSwap.stablecoinType, "Stablecoin types must match");
        require(offers[offerID].amountLowerBound == newSwap.amountLowerBound, "Lower bounds must match");
        require(offers[offerID].amountUpperBound == newSwap.amountUpperBound, "Upper bounds must match");
        require(offers[offerID].securityDepositAmount == newSwap.securityDepositAmount, "Security deposit amounts must match");
        require(offers[offerID].amountLowerBound <= newSwap.takenSwapAmount, "Swap amount must be >= lower bound of offer amount");
        require(offers[offerID].amountUpperBound >= newSwap.takenSwapAmount, "Swap amount must be <= upper bound of offer amount");
        require(offers[offerID].direction == newSwap.direction, "Directions must match");
        require(keccak256(offers[offerID].price) == keccak256(newSwap.price), "Prices must match");
        require(offers[offerID].paymentMethod == newSwap.paymentMethod, "Payment methods must match");
        require(offers[offerID].protocolVersion == newSwap.protocolVersion, "Protocol versions must match");
        require(offers[offerID].extraData == newSwap.makerExtraData, "Maker extra data must match");

        //Find proper stablecoin contract
        ERC20 token;

        if(newSwap.stablecoinType == StablecoinType.DAI) {
            token = ERC20(daiAddress);
        } else if (newSwap.stablecoinType == StablecoinType.USDC) {
            token = ERC20(usdcAddress);
        } else if (newSwap.stablecoinType == StablecoinType.BUSD) {
            token = ERC20(busdAddress);
        } else if (newSwap.stablecoinType == StablecoinType.USDT) {
            token = ERC20(usdtAddress);
        } else {
            revert("You must specify a supported stablecoin");
        }

        //Calculate required total amount
        newSwap.serviceFeeAmount = SafeMath.div(newSwap.takenSwapAmount, 100);
        uint256 totalAmount;
        if(newSwap.direction == SwapDirection.SELL) {
            //Taker is Buyer
            totalAmount = SafeMath.add(newSwap.securityDepositAmount, newSwap.serviceFeeAmount);
        } else if (newSwap.direction == SwapDirection.BUY) {
            //Taker is seller
            totalAmount = SafeMath.add(SafeMath.add(newSwap.takenSwapAmount, newSwap.securityDepositAmount), newSwap.serviceFeeAmount);
        } else {
            revert("You must specify a supported direction");
        }
        //Lock required total amount in escrow
        require(totalAmount <= token.allowance(msg.sender, address(this)), "Token allowance must be >= required amount");
        require(token.transferFrom(msg.sender, address(this), totalAmount), "Token transfer to Commuto Protocol failed");

        //Finish swap creation and notify that offer is taken
        newSwap.isCreated = true;
        newSwap.taker = msg.sender;
        offers[offerID].isTaken = true;
        newSwap.isPaymentSent = false;
        newSwap.isPaymentReceived = false;
        newSwap.hasBuyerClosed = false;
        newSwap.hasSellerClosed = false;
        swaps[offerID] = newSwap;
        emit OfferTaken(offerID);
    }

    //Report payment sent for swap
    function reportPaymentSent(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "A swap with the specified id does not exist");
        require(swaps[swapID].isPaymentSent == false, "Payment sending has already been reported for swap with specified id");
        if(swaps[swapID].direction == SwapDirection.BUY) {
            require(swaps[swapID].maker == msg.sender, "Payment sending can only be reported by buyer");
        } else if (swaps[swapID].direction == SwapDirection.SELL) {
            require(swaps[swapID].taker == msg.sender, "Payment sending can only be reported by buyer");
        } else {
            revert("Swap has invalid direction");
        }

        //Mark payment sent and notify
        swaps[swapID].isPaymentSent = true;
        emit PaymentSent(swapID);
    }

    //Report payment received for swap
    function reportPaymentReceived(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "A swap with the specified id does not exist");
        require(swaps[swapID].isPaymentSent, "Payment sending has not been reported for swap with specified id");
        require(swaps[swapID].isPaymentReceived == false, "Payment receiving has already been reported for swap with specified id");
        if(swaps[swapID].direction == SwapDirection.BUY) {
            require(swaps[swapID].taker == msg.sender, "Payment receiving can only be reported by seller");
        } else if (swaps[swapID].direction == SwapDirection.SELL) {
            require(swaps[swapID].maker == msg.sender, "Payment receiving can only be reported by seller");
        } else {
            revert("Swap has invalid direction");
        }

        //Mark payment received and notify
        swaps[swapID].isPaymentReceived = true;
        emit PaymentReceived(swapID);
    }

    //Close swap and receive STBL from escrow
    function closeSwap(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "A swap with the specified id does not exist");
        require(swaps[swapID].isPaymentReceived, "Payment receiving has not been reported for swap with specified id");

        //Find proper stablecoin contract
        ERC20 token;

        if(swaps[swapID].stablecoinType == StablecoinType.DAI) {
            token = ERC20(daiAddress);
        } else if (swaps[swapID].stablecoinType == StablecoinType.USDC) {
            token = ERC20(usdcAddress);
        } else if (swaps[swapID].stablecoinType == StablecoinType.BUSD) {
            token = ERC20(busdAddress);
        } else if (swaps[swapID].stablecoinType == StablecoinType.USDT) {
            token = ERC20(usdtAddress);
        } else {
            revert("You must specify a supported stablecoin");
        }

        uint256 returnAmount;

        //If caller is buyer and taker, return security deposit and swap amount, and send service fee to pool
        if(swaps[swapID].direction == SwapDirection.SELL && swaps[swapID].taker == msg.sender) {
            require(swaps[swapID].hasBuyerClosed == false, "Buyer has already closed swap");
            returnAmount = SafeMath.add(swaps[swapID].securityDepositAmount, swaps[swapID].takenSwapAmount);
            require(token.transfer(swaps[swapID].taker, returnAmount), "Token transfer failed");
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "Service fee transfer failed");
            swaps[swapID].hasBuyerClosed = true;
            emit BuyerClosed(swapID);
        }
        //If caller is buyer and maker, return security deposit, swap amount, and serviceFeeUpperBound - serviceFeeAmount, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.BUY && swaps[swapID].maker == msg.sender) {
            require(swaps[swapID].hasBuyerClosed == false, "Buyer has already closed swap");
            uint256 serviceFeeAmountUpperBound = SafeMath.div(swaps[swapID].amountUpperBound, 100);
            returnAmount = SafeMath.add(SafeMath.add(swaps[swapID].securityDepositAmount, swaps[swapID].takenSwapAmount), SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount));
            require(token.transfer(swaps[swapID].maker, returnAmount), "Token transfer failed");
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "Service fee transfer failed");
            swaps[swapID].hasBuyerClosed = true;
            emit BuyerClosed(swapID);
        }
        //If caller is seller and taker, return security deposit, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.BUY && swaps[swapID].taker == msg.sender) {
            require(swaps[swapID].hasSellerClosed == false, "Seller has already closed swap");
            returnAmount = swaps[swapID].securityDepositAmount;
            require(token.transfer(swaps[swapID].taker, returnAmount), "Token transfer failed");
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "Service fee transfer failed");
            swaps[swapID].hasSellerClosed = true;
            emit SellerClosed(swapID);
        }
        //If caller is seller and maker, return amountUpperBound - takenSwapAmount, security deposit and serviceFeeUpperBound - serviceFeeAmount, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.SELL && swaps[swapID].maker == msg.sender) {
            require(swaps[swapID].hasSellerClosed == false, "Seller has already closed swap");
            uint256 swapRemainder = SafeMath.sub(swaps[swapID].amountUpperBound, swaps[swapID].takenSwapAmount);
            uint256 serviceFeeAmountUpperBound = SafeMath.div(swaps[swapID].amountUpperBound, 100);
            returnAmount = SafeMath.add(SafeMath.add(swapRemainder, swaps[swapID].securityDepositAmount), SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount));
            require(token.transfer(swaps[swapID].taker, returnAmount), "Token transfer failed");
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "Service fee transfer failed");
            swaps[swapID].hasSellerClosed = true;
            emit SellerClosed(swapID);
        } else {
            revert("Only swap maker or taker can call this function");
        }
    }
}