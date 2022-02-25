// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

interface IOrumRevenue {
    // --- Events ---
    event CommitAdmin(address admin);
    event ApplyAdmin(address admin);
    event ToggleAllowCheckpointToken(bool toggleFlag);
    event CheckpointToken(uint time, uint tokens);
    event Claimed(address indexed recipient, uint amount, uint claimEpoch, uint maxEpoch);

    // --- Functions ---
    function checkpointToken() external;
    function veForAt(address _user, uint _timestamp) external view returns (uint);
    function checkpointTotalSupply() external;
    function claimable(address _addr) external view returns (uint);
    function applyAdmin() external;
    function commitAdmin(address _addr) external;
    function toggleAllowCheckpointToken() external;
    
}