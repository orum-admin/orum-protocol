// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

interface ITreasury{
    // --- Events ---
    event BorrowerOpsAddressChanged(address _newBorrowerOpsAddress);
    event VaultManagerAddressChanged(address _newVaultManagerAddress);
    event TreasuryROSEBalanceUpdated(uint _ROSE);

    // --- Functions ---
    function getROSEBalance() view external returns(uint);
}