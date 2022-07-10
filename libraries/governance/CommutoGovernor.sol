// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts/governance/Governor.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorVotesQuorumFraction.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorPreventLateQuorum.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorTimelockControl.sol";

// TODO: Add revenue transfer function
contract CommutoGovernor is Governor, GovernorVotes, GovernorVotesQuorumFraction, GovernorPreventLateQuorum, GovernorCountingSimple, GovernorTimelockControl {

    uint256 public proposalThresholdValue;

    constructor (IVotes commutoToken, TimelockController _timelock, uint256 quorumFraction, uint64 initialVoteExtension, uint256 _proposalThreshold)
        Governor("CommutoGovernor")
        GovernorVotes(commutoToken)
        GovernorVotesQuorumFraction(quorumFraction) // percentage of all issued tokens that must be used to abstain or vote in favor
        GovernorPreventLateQuorum(initialVoteExtension) // the number of blocks that are required to pass since a proposal reaches quorum until its voting period ends
        GovernorTimelockControl(_timelock)
    {
        proposalThresholdValue = _proposalThreshold;
    }

    function votingDelay() public pure override returns (uint256) {
        return 28800; // 1 day on BSC
    }

    function votingPeriod() public pure override returns (uint256) {
        return 201600; // 1 week on BSC
    }

    function proposalThreshold() public view override returns (uint256) {
        return proposalThresholdValue;
    }

    //Overrides required by solidity

    function _castVote(uint256 proposalId, address account, uint8 support, string memory reason)
        internal
        override(Governor, GovernorPreventLateQuorum)
        returns (uint256)
    {
        return super._castVote(proposalId, account, support, reason);
    }

    function proposalDeadline(uint256 proposalId)
        public
        view
        override(IGovernor, Governor, GovernorPreventLateQuorum)
        returns (uint256)
    {
        return super.proposalDeadline(proposalId);
    }

    function quorum(uint256 blockNumber)
        public
        view
        override(IGovernor, GovernorVotesQuorumFraction)
        returns (uint256)
    {
        return super.quorum(blockNumber);
    }

    function getVotes(address account, uint256 blockNumber)
        public
        view
        override(IGovernor, GovernorVotes)
        returns (uint256)
    {
        return super.getVotes(account, blockNumber);
    }

    function state(uint256 proposalId)
        public
        view
        override(Governor, GovernorTimelockControl)
        returns (ProposalState)
    {
        return super.state(proposalId);
    }

    function propose(address[] memory targets, uint256[] memory values, bytes[] memory calldatas, string memory description)
        public
        override(Governor, IGovernor)
        returns (uint256)
    {
        return super.propose(targets, values, calldatas, description);
    }

    function _execute(uint256 proposalId, address[] memory targets, uint256[] memory values, bytes[] memory calldatas, bytes32 descriptionHash)
        internal
        override(Governor, GovernorTimelockControl)
    {
        super._execute(proposalId, targets, values, calldatas, descriptionHash);
    }

    function _cancel(address[] memory targets, uint256[] memory values, bytes[] memory calldatas, bytes32 descriptionHash)
        internal
        override(Governor, GovernorTimelockControl)
        returns (uint256)
    {
        return super._cancel(targets, values, calldatas, descriptionHash);
    }

    function _executor()
        internal
        view
        override(Governor, GovernorTimelockControl)
        returns (address)
    {
        return super._executor();
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(Governor, GovernorTimelockControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
