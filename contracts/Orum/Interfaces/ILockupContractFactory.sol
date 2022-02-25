// SPDX-License-Identifier: MIT

pragma solidity >= 0.8.0;
    
interface ILockupContractFactory {
    
    // --- Events ---

    event OrumTokenAddressSet(address _orumTokenAddress);
    event LockupContractDeployedThroughFactory(address _lockupContractAddress, address _beneficiary, uint _unlockTime, address _deployer);

    // --- Functions ---

    function setOrumTokenAddress(address _orumTokenAddress) external;

    function deployLockupContract(address _beneficiary, uint _unlockTime) external;

    function isRegisteredLockup(address _addr) external view returns (bool);
}
