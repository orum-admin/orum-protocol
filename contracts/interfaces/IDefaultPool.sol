// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import "./IPool.sol";


interface IDefaultPool is IPool {
    // --- Events ---
    event VaultManagerAddressChanged(address _newVaultManagerAddress);
    event DefaultPoolOSDDebtUpdated(uint _OSDDebt);
    event DefaultPoolROSEBalanceUpdated(uint _ROSE);

    // --- Functions ---
    function sendROSEToActivePool(uint _amount) external;
}