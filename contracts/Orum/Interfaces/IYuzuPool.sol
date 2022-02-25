// SPDX-License-Identifier: MIT

pragma solidity >= 0.8.0;


interface IYuzuPool {

    event OrumTokenAddressChanged(address _orumTokenAddress);
    event YuzuTokenAddressChanged(address _yuzuTokenAddress);
    event RewardAdded(uint256 reward);
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);
    
    function setParams(address _orumTokenAddress, address _yuzuTokenAddress, uint256 _duration) external;
    function lastTimeRewardApplicable() external view returns (uint256);
    function rewardPerToken() external view returns (uint256);
    function earned(address account) external view returns (uint256);
    function withdrawAndClaim() external;
    function claimReward() external;
    //function notifyRewardAmount(uint256 reward) external;
    
}