//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase {
    address payable[] public players;
    address payable public latestWinner;
    address owner;
    event RequestedRandomness(bytes32 requestId);

    // To keep track of the recent randomness.
    uint256 public randomNo;
    uint256 public entranceFees;
    AggregatorV3Interface internal ethUSDPriceFeed;
    enum LotteryState {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LotteryState public LS;
    uint256 public fee;
    bytes32 public keyHash;

    constructor(
        address _priceFeed,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyHash
    ) VRFConsumerBase(_vrfCoordinator, _link) {
        entranceFees = 50 * (10**18);
        ethUSDPriceFeed = AggregatorV3Interface(_priceFeed);
        LS = LotteryState.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
        owner = msg.sender;
    }

    function enter() public payable {
        // $5 dolars minimum
        require(LS == LotteryState.OPEN, "Cannot enter to the lottery now");
        require(msg.value >= getEntranceFee(), "Entrance fees not enough");

        // sender in 0.8 is not automatically payable.
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUSDPriceFeed.latestRoundData();
        uint256 convertedPrice = uint256(price) * 10**18; // 18 decimals
        uint256 costToEnter = (entranceFees * 10**18) / convertedPrice;
        return costToEnter;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "You don't have the access");
        _;
    }

    function startLottery() public onlyOwner {
        require(LS == LotteryState.CLOSED);
        LS = LotteryState.OPEN;
    }

    function endLottery() public onlyOwner {
        LS = LotteryState.CALCULATING_WINNER;
        bytes32 requestedId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestedId);
    }

    // The random number comes with request and recieve mechanism
    // we request randomness with requestRansomness function and we get response in fulfillRandomness function
    function fulfillRandomness(bytes32 _requested, uint256 _randomness)
        internal
        override
    {
        require(LS == LotteryState.CALCULATING_WINNER, "Not allowed");
        require(_randomness > 0, "Random number not found");
        uint256 indexOfWinner = _randomness % players.length;
        latestWinner = players[indexOfWinner];
        latestWinner.transfer(address(this).balance);

        //Reset
        players = new address payable[](0);
        LS = LotteryState.CLOSED;
        randomNo = _randomness;
    }
}
