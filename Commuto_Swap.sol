// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.0/contracts/token/ERC20/ERC20.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.0/contracts/math/SafeMath.sol";

//TODO: Better code comments
contract Commuto_Swap {
    
    address public owner;
    //TODO: Deal with decimal point precision differences between stablecoins
    address public daiAddress = 0xd9145CCE52D386f254917e481eB44e9943F39138; //The address of a ERC20 contract to represent DAI
    address public usdcAddress = 0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8; //The address of a ERC20 contract to represent USDC
    address public busdAddress = 0xf8e81D47203A594245E36C48e151709F0C19fBe8; //The address of a ERC20 contract to represent BUSD
    address public usdtAddress = 0xD7ACd2a9FD159E69Bb102A1ca21C9a3e3A5F771B; //The address of a ERC20 contract to represent USDT
    
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
    
    event OfferOpened(bytes16 offerID);
    
    mapping (bytes16 => Offer) private offers;
    
    constructor () public {
        owner = msg.sender;
    }
    //TODO: Write tests
    //TODO: Test duplicate id prevention
    //TODO: Test non-zero lower bound protection
    //TODO: Test upper bound larger than lower bound protection
    //TODO: Test security deposit amount protection
    //TODO: Test service fee amount protection
    //TODO: Test offer protocol protection
    //TODO: Test stablecoin type protection
    //TODO: Test stablecoin allowance check
    //TODO: Test OfferOpened event emittance
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
        
        uint256 serviceFeeAmountUpperBound = newOffer.amountUpperBound / 100;
        uint256 totalAmount;
        if(newOffer.direction == SwapDirection.SELL) {
            totalAmount = SafeMath.add(SafeMath.add(newOffer.amountUpperBound, newOffer.securityDepositAmount), serviceFeeAmountUpperBound);
        } else if (newOffer.direction == SwapDirection.BUY) {
            totalAmount = SafeMath.add(newOffer.securityDepositAmount, serviceFeeAmountUpperBound);
        } else {
            revert("You must specify a supported direction");
        }
        require(totalAmount >= token.allowance(msg.sender, address(this)), "Token allowance must be greater than total swap amount, including maximum swap amount, security deposit and max service fee");
        require(token.transferFrom(msg.sender, address(this), totalAmount), "Token transfer to Commuto Protocol failed");
        
        newOffer.isCreated = true;
        newOffer.maker = msg.sender;
        offers[offerID] = newOffer;
        emit OfferOpened(offerID);
    }
}