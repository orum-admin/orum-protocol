// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

interface ICollSurplusPool {

    // --- Events ---
    
    event BorrowerOpsAddressChanged(address _newBorrowerOpsAddress);
    event VaultManagerAddressChanged(address _newVaultManagerAddress);
    event ActivePoolAddressChanged(address _newActivePoolAddress);

    event CollBalanceUpdated(address indexed _account, uint _newBalance);
    event RoseSent(address _to, uint _amount);

    // --- Contract setters ---

    function setAddresses(
        address _borrowerOpsAddress,
        address _VaultManagerAddress,
        address _activePoolAddress
    ) external;

    function getROSE() external view returns (uint);

    function getCollateral(address _account) external view returns (uint);

    function accountSurplus(address _account, uint _amount) external;

    function claimColl(address _account) external;
}