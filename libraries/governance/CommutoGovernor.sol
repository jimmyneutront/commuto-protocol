// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "../../node_modules/@openzeppelin/contracts/governance/Governor.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorVotesQuorumFraction.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";
import "../../node_modules/@openzeppelin/contracts/governance/extensions/GovernorTimelockControl.sol";


contract CommutoGovernor is Governor, GovernorVotes, GovernorVotesQuorumFraction, GovernorCountingSimple, GovernorTimelockControl {
    constructor (IVotes commutoToken, TimelockController _timelock)
        Governor("CommutoGovernor")
        GovernorVotes(commutoToken)
        GovernorVotesQuorumFraction(4) //4% of all issued tokens must be used to abstain or vote in favor
        GovernorTimelockControl(_timelock)
    {}

    function votingDelay() public pure override returns (uint256) {
        return 28800; // 1 day on BSC
    }

    function votingPeriod() public pure override returns (uint256) {
        return 201600; // 1 week on BSC
    }

    function proposalThreshold() public pure override returns (uint256) {
        return 0;
    }

    //Overrides required by solidity

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