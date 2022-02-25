// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

// Common interface for the Pools.
interface IPool {
    
    // --- Events ---
    
    event ROSEBalanceUpdated(uint _newBalance);
    event OSDBalanceUpdated(uint _newBalance);
    event ActivePoolAddressChanged(address _newActivePoolAddress);
    event DefaultPoolAddressChanged(address _newDefaultPoolAddress);
    event StabilityPoolAddressChanged(address _newStabilityPoolAddress);
    event RoseSent(address _to, uint _amount);

    // --- Functions ---
    
    function getROSE() external view returns (uint);

    function getOSDDebt() external view returns (uint);

    function increaseOSDDebt(uint _amount) external;

    function decreaseOSDDebt(uint _amount) external;
}