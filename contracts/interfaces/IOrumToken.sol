// SPDX-License-Identifier: MIT

pragma solidity >= 0.8.0;

import "./IERC20.sol";
import "./IERC2612.sol";


interface IOrumToken is IERC20, IERC2612 {
   
    // --- Events ---
    
    event CommunityIssuanceAddressSet(address _communityIssuanceAddress);
    event LockupContractFactoryAddressSet(address _lockupContractFactoryAddress);

    // --- Functions ---

    function getDeploymentStartTime() external view returns (uint256);

    function getLpRewardsEntitlement() external view returns (uint256);
}