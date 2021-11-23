// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

//import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.0/contracts/math/SafeMath.sol";
import "SafeMath.sol";

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

//TODO: Only charge security deposit amount when making offer, and allow funding only once taken
//TODO: Support adding supported ERC20 tokens by governance vote
//TODO: Deal with contract size limitation
//TODO: Better code comments
contract CommutoSwap {
    
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

    /*A mapping of settlement method names to boolean values indicating whether they are supported or not, and an array
    containing the names of all supported settlement methods. Both a mapping and an array are necessary because map
    value lookups are inexpensive and keep user costs down, but an array is necessary so that one can always obtain a
    complete list of supported settlement methods.
    */
    mapping (bytes => bool) private settlementMethods;
    bytes[] private supportedSettlementMethods;

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
    
    struct Offer {
        bool isCreated;
        bool isTaken;
        address maker;
        bytes interfaceId;
        StablecoinType stablecoinType;
        uint256 amountLowerBound;
        uint256 amountUpperBound;
        uint256 securityDepositAmount;
        SwapDirection direction;
        bytes price;
        bytes[] settlementMethods;
        uint256 protocolVersion;
        bytes32 extraData;
    }

    struct Swap {
        bool isCreated;
        address maker;
        bytes makerInterfaceId;
        address taker;
        bytes takerInterfaceId;
        StablecoinType stablecoinType;
        uint256 amountLowerBound;
        uint256 amountUpperBound;
        uint256 securityDepositAmount;
        uint256 takenSwapAmount;
        uint256 serviceFeeAmount;
        SwapDirection direction;
        bytes price;
        bytes settlementMethod;
        uint256 protocolVersion;
        bytes32 makerExtraData;
        bytes32 takerExtraData;
        bool isPaymentSent;
        bool isPaymentReceived;
        bool hasBuyerClosed;
        bool hasSellerClosed;
    }
    
    event OfferOpened(bytes16 offerID, bytes interfaceId);
    event PriceChanged(bytes16 offerID);
    event OfferCanceled(bytes16 offerID);
    event OfferTaken(bytes16 offerID, bytes takerInterfaceId);
    event PaymentSent(bytes16 swapID);
    event PaymentReceived(bytes16 swapID);
    event BuyerClosed(bytes16 swapID);
    event SellerClosed(bytes16 swapID);
    
    mapping (bytes16 => Offer) private offers;
    mapping (bytes16 => mapping (bytes => bool)) private offerSettlementMethods;
    mapping (bytes16 => Swap) private swaps;

    function getOffer(bytes16 offerID) view public returns (Offer memory) {
        return offers[offerID];
    }

    function getSwap(bytes16 swapID) view public returns (Swap memory) {
        return swaps[swapID];
    }
    
    constructor (address _serviceFeePool,
                 address _daiAddress,
                 address _usdcAddress,
                 address _busdAddress,
                 address _usdtAddress) public {
        owner = msg.sender;
        require(_serviceFeePool != address(0), "e0"); //"e0": "_serviceFeePool address cannot be zero"
        serviceFeePool = _serviceFeePool;
        require(_daiAddress != address(0), "e1"); //"e1": "_daiAddress cannot be zero address"
        daiAddress = _daiAddress;
        require(_usdcAddress != address(0), "e2"); //"e2": "_usdcAddress cannot be zero address"
        usdcAddress = _usdcAddress;
        require(_busdAddress != address(0), "e3"); //"e3": "_busdAddress cannot be zero address"
        busdAddress = _busdAddress;
        require(_usdtAddress != address(0), "e4"); //"e4": "_usdtAddress cannot be zero address"
        usdtAddress = _usdtAddress;
    }

    //Create a new swap offer
    /*
    Note that openOffer will not prevent a maker from creating an offer with unsupported settlement methods, to keep gas
    costs low. However, a taker will not be able to take an offer with unsupported settlement methods, so the maker
    should be careful not to create such invalid offers.
    */
    function openOffer(bytes16 offerID, Offer memory newOffer) public {
        //Validate arguments
        require(!offers[offerID].isCreated, "e5"); //"An offer with the specified id already exists"
        require(newOffer.amountLowerBound > 0, "e6"); //"The minimum swap amount must be greater than zero"
        require(newOffer.amountUpperBound >= newOffer.amountLowerBound, "e7"); //"e7": "The maximum swap amount must be >= the minimum swap amount"
        require(SafeMath.mul(newOffer.securityDepositAmount, 10) >= newOffer.amountLowerBound, "e8"); //"e8": "The security deposit must be at least 10% of the minimum swap amount"
        uint256 serviceFeeAmountLowerBound = SafeMath.div(newOffer.amountLowerBound, 100);
        require(serviceFeeAmountLowerBound > 0, "e9"); //"e9": "Service fee amount must be greater than zero"
        require(newOffer.protocolVersion >= protocolVersion, "e10"); //"e10": "Offers can only be created for the most recent protocol version"
        
        //Find proper stablecoin contract
        /*
        Slither complains that "token" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because a supported stablecoin has not been specified.
        */
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
            revert("e11"); //"e11": "You must specify a supported stablecoin"
        }

        //Calculate required total amount
        uint256 serviceFeeAmountUpperBound = SafeMath.div(newOffer.amountUpperBound, 100);
        /*
        Slither complains that "totalAmount" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because a supported direction has not been specified.
        */
        uint256 totalAmount;
        if(newOffer.direction == SwapDirection.SELL) {
            totalAmount = SafeMath.add(SafeMath.add(newOffer.amountUpperBound, newOffer.securityDepositAmount), serviceFeeAmountUpperBound);
        } else if (newOffer.direction == SwapDirection.BUY) {
            totalAmount = SafeMath.add(newOffer.securityDepositAmount, serviceFeeAmountUpperBound);
        } else {
            revert("e12"); //"e12": "You must specify a supported direction"
        }

        //Finish and notify of offer creation
        newOffer.isCreated = true;
        newOffer.isTaken = false;
        newOffer.maker = msg.sender;
        offers[offerID] = newOffer;
        //Record supported settlement methods
        for (uint i = 0; i < newOffer.settlementMethods.length; i++) {
            offerSettlementMethods[offerID][newOffer.settlementMethods[i]] = true;
        }
        emit OfferOpened(offerID, newOffer.interfaceId);

        //Lock required total amount in escrow
        require(totalAmount <= token.allowance(msg.sender, address(this)), "e13"); //"e13": "Token allowance must be >= required amount"
        require(token.transferFrom(msg.sender, address(this), totalAmount), "e14"); //"e14": "Token transfer to Commuto Protocol failed"
    }

    //Edit the price and supported settlement methods of an open swap offer
    function editOffer(bytes16 offerID, Offer memory editedOffer, bool editPrice, bool editSettlementMethods) public {
        //Validate arguments
        require(offers[offerID].isCreated, "e15"); //"e15": "An offer with the specified id does not exist"
        require(!offers[offerID].isTaken, "e16"); //"e16": "Offer is taken and cannot be mutated"
        require(offers[offerID].maker == msg.sender, "e17"); //"e17": "Offers can only be mutated by offer maker"

        if (editPrice) {
            offers[offerID].price = editedOffer.price;
        }

        if (editSettlementMethods) {
            //Delete records of supported settlement methods in preparation for updated info
            for (uint i = 0; i < offers[offerID].settlementMethods.length; i++) {
                offerSettlementMethods[offerID][offers[offerID].settlementMethods[i]] = false;
            }
            //Record new supported settlement methods
            for (uint i = 0; i < editedOffer.settlementMethods.length; i++) {
                offerSettlementMethods[offerID][editedOffer.settlementMethods[i]] = true;
            }
            offers[offerID].settlementMethods = editedOffer.settlementMethods;
        }
    }

    //Cancel open swap offer
    function cancelOffer(bytes16 offerID) public {
        //Validate arguments
        require(offers[offerID].isCreated, "e15"); //"e15": "An offer with the specified id does not exist"
        require(!offers[offerID].isTaken, "e16"); //"e16": "Offer is taken and cannot be mutated"
        require(offers[offerID].maker == msg.sender, "e17"); //"e17": "Offers can only be mutated by offer maker"

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
            revert("e11"); //"e11": "You must specify a supported stablecoin"
        }

        //Calculate total amount in escrow
        uint256 serviceFeeAmountUpperBound = SafeMath.div(offers[offerID].amountUpperBound, 100);
        /*
        Slither complains that "totalAmount" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because the specified offer has an invalid direction.
        */
        uint256 totalAmount;
        if(offers[offerID].direction == SwapDirection.SELL) {
            totalAmount = SafeMath.add(SafeMath.add(offers[offerID].amountUpperBound, offers[offerID].securityDepositAmount), serviceFeeAmountUpperBound);
        } else if (offers[offerID].direction == SwapDirection.BUY) {
            totalAmount = SafeMath.add(offers[offerID].securityDepositAmount, serviceFeeAmountUpperBound);
        } else {
            revert("e18"); //"e18": "Offer has invalid direction"
        }

        //Delete offer, refund STBL and notify
        delete offers[offerID];
        //Delete records of supported settlement methods
        for (uint i = 0; i < offers[offerID].settlementMethods.length; i++) {
            offerSettlementMethods[offerID][offers[offerID].settlementMethods[i]] = false;
        }
        emit OfferCanceled(offerID);
        require(token.transfer(offers[offerID].maker, totalAmount), "e19"); //"e19": "Token transfer failed"
    }

    //Take a swap offer
    function takeOffer(bytes16 offerID, Swap memory newSwap) public {
        //Validate arguments
        require(offers[offerID].isCreated, "e15"); //"e15": "An offer with the specified id does not exist",
        require(!swaps[offerID].isCreated, "e20"); //"e20": "The offer with the specified id has already been taken"
        require(offers[offerID].maker == newSwap.maker, "e21"); //"e21": "Maker addresses must match"
        require(sha256(offers[offerID].interfaceId) == sha256(newSwap.makerInterfaceId), "e21.1"); //"e21.1": "Maker interface ids must match",
        require(offers[offerID].stablecoinType == newSwap.stablecoinType, "e22"); //"e22": "Stablecoin types must match"
        require(offers[offerID].amountLowerBound == newSwap.amountLowerBound, "e23"); //"e23": "Lower bounds must match"
        require(offers[offerID].amountUpperBound == newSwap.amountUpperBound, "e24"); //"e24": "Upper bounds must match"
        require(offers[offerID].securityDepositAmount == newSwap.securityDepositAmount, "e25"); //"e25": "Security deposit amounts must match"
        require(offers[offerID].amountLowerBound <= newSwap.takenSwapAmount, "e26"); //"e26": "Swap amount must be >= lower bound of offer amount"
        require(offers[offerID].amountUpperBound >= newSwap.takenSwapAmount, "e27"); //"e27": "Swap amount must be <= upper bound of offer amount"
        require(offers[offerID].direction == newSwap.direction, "e28"); //"e28": "Directions must match"
        require(sha256(offers[offerID].price) == sha256(newSwap.price), "e29"); //"e29": "Prices must match"
        require(settlementMethods[newSwap.settlementMethod] == true, "e46"); //"e46": "Settlement method must be supported"
        require(offerSettlementMethods[offerID][newSwap.settlementMethod] == true, "e30"); //"e30": "Settlement method must be accepted by maker"
        require(offers[offerID].protocolVersion == newSwap.protocolVersion, "e31"); //"e31": "Protocol versions must match"
        require(offers[offerID].extraData == newSwap.makerExtraData, "e32"); //"e32": "Maker extra data must match"

        //Find proper stablecoin contract
        /*
        Slither complains that "token" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because a supported stablecoin has not been specified.
        */
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
            revert("e11"); //"e11": "You must specify a supported stablecoin"
        }

        //Calculate required total amount
        newSwap.serviceFeeAmount = SafeMath.div(newSwap.takenSwapAmount, 100);
        /*
        Slither complains that "totalAmount" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because a supported direction has not been specified.
        */
        uint256 totalAmount;
        if(newSwap.direction == SwapDirection.SELL) {
            //Taker is Buyer
            totalAmount = SafeMath.add(newSwap.securityDepositAmount, newSwap.serviceFeeAmount);
        } else if (newSwap.direction == SwapDirection.BUY) {
            //Taker is seller
            totalAmount = SafeMath.add(SafeMath.add(newSwap.takenSwapAmount, newSwap.securityDepositAmount), newSwap.serviceFeeAmount);
        } else {
            revert("e12"); //"e12": "You must specify a supported direction"
        }

        //Finish swap creation and notify that offer is taken
        newSwap.isCreated = true;
        newSwap.taker = msg.sender;
        offers[offerID].isTaken = true;
        newSwap.isPaymentSent = false;
        newSwap.isPaymentReceived = false;
        newSwap.hasBuyerClosed = false;
        newSwap.hasSellerClosed = false;
        swaps[offerID] = newSwap;
        emit OfferTaken(offerID, newSwap.takerInterfaceId);

        //Lock required total amount in escrow
        require(totalAmount <= token.allowance(msg.sender, address(this)), "e13"); //"e13": "Token allowance must be >= required amount"
        require(token.transferFrom(msg.sender, address(this), totalAmount), "e14"); //"e14": "Token transfer to Commuto Protocol failed"
    }

    //Report payment sent for swap
    function reportPaymentSent(bytes16 swapID) public {
        //Validate arguments
        require(swaps[swapID].isCreated, "e33"); //"e33": "A swap with the specified id does not exist"
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
        /*
        Slither complains that "token" is never initialized. However, compilation fails if this declaration takes place
        within the if/else statements, so it must remain here. Additionally, if initialization doesn't take place within
        the if/else statements, the function reverts because a supported stablecoin has not been specified.
        */
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
            revert("e11"); //"e11": "You must specify a supported stablecoin"
        }

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
        //If caller is seller and maker, return amountUpperBound - takenSwapAmount, security deposit and serviceFeeUpperBound - serviceFeeAmount, and send service fee to pool
        else if (swaps[swapID].direction == SwapDirection.SELL && swaps[swapID].maker == msg.sender) {
            require(!swaps[swapID].hasSellerClosed, "e43"); //"e43": "Seller has already closed swap"
            uint256 swapRemainder = SafeMath.sub(swaps[swapID].amountUpperBound, swaps[swapID].takenSwapAmount);
            uint256 serviceFeeAmountUpperBound = SafeMath.div(swaps[swapID].amountUpperBound, 100);
            returnAmount = SafeMath.add(SafeMath.add(swapRemainder, swaps[swapID].securityDepositAmount), SafeMath.sub(serviceFeeAmountUpperBound, swaps[swapID].serviceFeeAmount));
            swaps[swapID].hasSellerClosed = true;
            emit SellerClosed(swapID);
            require(token.transfer(swaps[swapID].maker, returnAmount), "e19"); //"e19": "Token transfer failed"
            require(token.transfer(serviceFeePool, swaps[swapID].serviceFeeAmount), "e42"); //"e42": "Service fee transfer failed"
        } else {
            revert("e44"); //"e44": "Only swap maker or taker can call this function"
        }
    }
}