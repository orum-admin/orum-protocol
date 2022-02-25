// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import "./IERC20.sol";
import "./IERC2612.sol";

interface IOSDToken is IERC20, IERC2612 { 
    
    // --- Events ---

    event VaultManagerAddressChanged(address _vaultManagerAddress);
    event StabilityPoolAddressChanged(address _newStabilityPoolAddress);
    event BorrowerOpsAddressChanged(address _newBorrowerOpsAddress);

    event OSDTokenBalanceUpdated(address _user, uint _amount);

    // --- Functions ---

    function mint(address _account, uint256 _amount) external;

    function burn(address _account, uint256 _amount) external;

    function sendToPool(address _sender,  address poolAddress, uint256 _amount) external;

    function returnFromPool(address poolAddress, address user, uint256 _amount ) external;
}