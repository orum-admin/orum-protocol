// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

interface ICommunityIssuance { 
    
    // --- Events ---
    
    event OrumTokenAddressSet(address _orumTokenAddress);
    event StabilityPoolAddressSet(address _stabilityPoolAddress);
    event TotalOrumIssuedUpdated(uint _totalOrumIssued);

    // --- Functions ---

    function setAddresses(address _orumTokenAddress, address _stabilityPoolAddress) external;

    function issueOrum() external returns (uint);

    function sendOrum(address _account, uint _orumAmount) external;
}
