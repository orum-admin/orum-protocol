// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import "./IPool.sol";


interface IActivePool is IPool {
    // --- Events ---
    event BorrowerOpsAddressChanged(address _newBorrowerOpsAddress);
    event VaultManagerAddressChanged(address _newVaultManagerAddress);
    event ActivePoolOSDDebtUpdated(uint _OSDDebt);
    event ActivePoolROSEBalanceUpdated(uint _ROSE);

    // --- Functions ---
    function sendROSE(address _account, uint _amount) external;
}