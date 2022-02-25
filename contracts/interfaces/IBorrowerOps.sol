// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

interface IBorrowerOps {
    // --- Events ---
    event VaultManagerAddressChanged(address _newVaultManagerAddress);
    event ActivePoolAddressChanged(address _activePoolAddress);
    event DefaultPoolAddressChanged(address _defaultPoolAddress);
    event StabilityPoolAddressChanged(address _stabilityPoolAddress);
    event GasPoolAddressChanged(address _gasPoolAddress);
    event CollSurplusPoolAddressChanged(address _collSurplusPoolAddress);
    event PriceFeedAddressChanged(address  _newPriceFeedAddress);
    event SortedVaultsAddressChanged(address _sortedVaultsAddress);
    event OSDTokenAddressChanged(address _osdTokenAddress);
    event OrumRevenueAddressChanged(address _orumRevenueAddress);

    event VaultCreated(address indexed _borrower, uint arrayIndex);
    event VaultUpdated(address indexed _borrower, uint _debt, uint _coll, uint stake, uint8 operation);
    event BorrowFeeInROSE(address indexed _borrower, uint _borrowFee);
    event TEST_BorrowFeeSentToTreasury(address indexed _borrower, uint _borrowFee);
    event TEST_BorrowFeeSentToOrumRevenue(address indexed _borrower, uint _borrowFee);

    // --- Functions ---
    function openVault(uint _maxFee, uint _debtAmount, address _upperHint, address _lowerHint) external payable;
    function addColl(address _upperHint, address _lowerHint) external payable;
    function moveROSEGainToVault(address _user, address _upperHint, address _lowerHint) external payable;
    function withdrawColl(uint _amount, address _upperHint, address _lowerHint) external;
    function withdrawOSD(uint _maxFee, uint _amount, address _upperHint, address _lowerHint) external;
    function repayOSD(uint _amount, address _upperHint, address _lowerHint) external;
    function closeVault() external;
    function claimCollateral() external;
    function getCompositeDebt(uint _debt) external view returns (uint);
}