// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import "./interfaces/IBorrowerOps.sol";
import "./interfaces/IVaultManager.sol";
import "./interfaces/IOSDToken.sol";
import "./interfaces/ICollSurplusPool.sol";
import "./interfaces/ISortedVaults.sol";
import "./Dependencies/OrumBase.sol";
import "./Dependencies/CheckContract.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract BorrowerOps is OrumBase, Ownable, CheckContract, IBorrowerOps {
    string constant public NAME = "BorrowerOps";

    // --- Connected contract declarations ---

    IVaultManager public vaultManager;

    address stabilityPoolAddress;

    address gasPoolAddress;

    address orumFeeDistributionAddress;
    uint public lockupTime;

    ICollSurplusPool collSurplusPool;

    IOSDToken public osdToken;

    // A doubly linked list of Vaults, sorted by their collateral ratios
    ISortedVaults public sortedVaults;

    /* --- Variable container structs  ---
    Used to hold, return and assign variables inside a function, in order to avoid the error:
    "CompilerError: Stack too deep". */

     struct LocalVariables_adjustVault {
        uint price;
        uint collChange;
        uint netDebtChange;
        bool isCollIncrease;
        uint debt;
        uint coll;
        uint oldICR;
        uint newICR;
        uint newTCR;
        uint ROSEFee;
        uint newDebt;
        uint newColl;
        uint stake;
    }

    struct LocalVariables_openVault {
        uint price;
        uint ROSEFee;
        uint netColl;
        uint netDebt;
        uint compositeDebt;
        uint ICR;
        uint NICR;
        uint stake;
        uint arrayIndex;
    }

    struct ContractsCache {
        IVaultManager vaultManager;
        IActivePool activePool;
        IOSDToken osdToken;
    }

    enum BorrowerOperation {
        openVault,
        closeVault,
        adjustVault
    }

    // --- Dependency setters ---
    function setAddresses(
        address _vaultManagerAddress,
        address _activePoolAddress,
        address _defaultPoolAddress,
        address _stabilityPoolAddress,
        address _gasPoolAddress,
        address _collSurplusPoolAddress,
        address _priceFeedAddress,
        address _sortedVaultsAddress,
        address _osdTokenAddress,
        address _orumFeeDistributionAddress
    )
        external
        onlyOwner
    {
        // This makes impossible to open a vault with zero withdrawn OSD
        assert(MIN_NET_DEBT > 0);

        checkContract(_vaultManagerAddress);
        checkContract(_activePoolAddress);
        checkContract(_defaultPoolAddress);
        checkContract(_stabilityPoolAddress);
        checkContract(_gasPoolAddress);
        checkContract(_collSurplusPoolAddress);
        checkContract(_priceFeedAddress);
        checkContract(_sortedVaultsAddress);
        checkContract(_osdTokenAddress);
        // checkContract(_orumFeeDistributionAddress);

        vaultManager = IVaultManager(_vaultManagerAddress);
        activePool = IActivePool(_activePoolAddress);
        defaultPool = IDefaultPool(_defaultPoolAddress);
        stabilityPoolAddress = _stabilityPoolAddress;
        gasPoolAddress = _gasPoolAddress;
        collSurplusPool = ICollSurplusPool(_collSurplusPoolAddress);
        priceFeed = IPriceFeed(_priceFeedAddress);
        sortedVaults = ISortedVaults(_sortedVaultsAddress);
        osdToken = IOSDToken(_osdTokenAddress);
        orumFeeDistributionAddress = _orumFeeDistributionAddress;

        emit VaultManagerAddressChanged(_vaultManagerAddress);
        emit ActivePoolAddressChanged(_activePoolAddress);
        emit DefaultPoolAddressChanged(_defaultPoolAddress);
        emit StabilityPoolAddressChanged(_stabilityPoolAddress);
        emit GasPoolAddressChanged(_gasPoolAddress);
        emit CollSurplusPoolAddressChanged(_collSurplusPoolAddress);
        emit PriceFeedAddressChanged(_priceFeedAddress);
        emit SortedVaultsAddressChanged(_sortedVaultsAddress);
        emit OSDTokenAddressChanged(_osdTokenAddress);
        emit OrumRevenueAddressChanged(_orumFeeDistributionAddress);
    }

    // --- Borrower Vault Ops ---

    function openVault(uint _maxFeePercentage, uint _OSDAmount, address _upperHint, address _lowerHint) external payable override {
        ContractsCache memory contractsCache = ContractsCache(vaultManager, activePool, osdToken);
        LocalVariables_openVault memory vars;

        vars.price = priceFeed.fetchPrice();
        bool isRecoveryMode = _checkRecoveryMode(vars.price);

        _requireValidMaxFeePercentage(_maxFeePercentage, isRecoveryMode);
        _requireVaultisNotActive(contractsCache.vaultManager, msg.sender);

        vars.netDebt = _OSDAmount;
        vars.netColl = msg.value;

        if (!isRecoveryMode) {
            vars.ROSEFee = _triggerBorrowingFee(contractsCache.vaultManager, _OSDAmount, _maxFeePercentage, vars.price);
            // send the rose fee to the staking contract
            (bool success_staking,) = orumFeeDistributionAddress.call{value: vars.ROSEFee}("");
            require(success_staking,"BorrowerOps: Borrow fee payment failed");
            vars.netColl -= vars.ROSEFee;
        }
        _requireAtLeastMinNetDebt(vars.netDebt);

        // ICR is based on the composite debt, i.e. the requested OSD amount + OSD borrowing fee + OSD gas comp.
        vars.compositeDebt = _getCompositeDebt(vars.netDebt);
        assert(vars.compositeDebt > 0);
        
        vars.ICR = OrumMath._computeCR(vars.netColl, vars.compositeDebt, vars.price);
        vars.NICR = OrumMath._computeNominalCR(vars.netColl, vars.compositeDebt);

        if (isRecoveryMode) {
            _requireICRisAboveCCR(vars.ICR);
        } else {
            _requireICRisAboveMCR(vars.ICR);
            uint newTCR = _getNewTCRFromVaultChange(vars.netColl, true, vars.compositeDebt, true, vars.ROSEFee, vars.price);  // bools: coll increase, debt increase
            _requireNewTCRisAboveCCR(newTCR); 
        }

        // Set the vault struct's properties
        contractsCache.vaultManager.setVaultStatus(msg.sender, 1);
        contractsCache.vaultManager.increaseVaultColl(msg.sender, vars.netColl);
        contractsCache.vaultManager.increaseVaultDebt(msg.sender, vars.compositeDebt);

        contractsCache.vaultManager.updateVaultRewardSnapshots(msg.sender);
        vars.stake = contractsCache.vaultManager.updateStakeAndTotalStakes(msg.sender);

        sortedVaults.insert(msg.sender, vars.NICR, _upperHint, _lowerHint);
        vars.arrayIndex = contractsCache.vaultManager.addVaultOwnerToArray(msg.sender);
        emit VaultCreated(msg.sender, vars.arrayIndex);

        // Move the rose to the Active Pool, and mint the OSDAmount to the borrower
        _activePoolAddColl(contractsCache.activePool, vars.netColl);
        _withdrawOSD(contractsCache.activePool, contractsCache.osdToken, msg.sender, _OSDAmount, vars.netDebt);
        // Move the OSD gas compensation to the Gas Pool
        _withdrawOSD(contractsCache.activePool, contractsCache.osdToken, gasPoolAddress, OSD_GAS_COMPENSATION, OSD_GAS_COMPENSATION);

        emit VaultUpdated(msg.sender, vars.compositeDebt, vars.netColl, vars.stake, uint8(BorrowerOperation.openVault));
        emit BorrowFeeInROSE(msg.sender, vars.ROSEFee);
    }

    // Send ROSE as collateral to a vault
    function addColl(address _upperHint, address _lowerHint) external payable override {
        _adjustVault(msg.sender, 0, 0, false, _upperHint, _lowerHint, 0);
    }

    // Send ROSE as collateral to a vault. Called by only the Stability Pool.
    function moveROSEGainToVault(address _borrower, address _upperHint, address _lowerHint) external payable override {
        _requireCallerIsStabilityPool();
        _adjustVault(_borrower, 0, 0, false, _upperHint, _lowerHint, 0);
    }

    // Withdraw ROSE collateral from a vault
    function withdrawColl(uint _collWithdrawal, address _upperHint, address _lowerHint) external override {
        _adjustVault(msg.sender, _collWithdrawal, 0, false, _upperHint, _lowerHint, 0);
    }

    // Withdraw OSD tokens from a vault: mint new OSD tokens to the owner, and increase the vault's debt accordingly
    function withdrawOSD(uint _maxFeePercentage, uint _OSDAmount, address _upperHint, address _lowerHint) external override {
        _adjustVault(msg.sender, 0, _OSDAmount, true, _upperHint, _lowerHint, _maxFeePercentage);
    }

    // Repay OSD tokens to a Vault: Burn the repaid OSD tokens, and reduce the vault's debt accordingly
    function repayOSD(uint _OSDAmount, address _upperHint, address _lowerHint) external override {
        _adjustVault(msg.sender, 0, _OSDAmount, false, _upperHint, _lowerHint, 0);
    }
    /*
    * _adjustVault(): Alongside a debt change, this function can perform either a collateral top-up or a collateral withdrawal. 
    *
    * It therefore expects either a positive msg.value, or a positive _collWithdrawal argument.
    *
    * If both are positive, it will revert.
    */
    function _adjustVault(address _borrower, uint _collWithdrawal, uint _OSDChange, bool _isDebtIncrease, address _upperHint, address _lowerHint, uint _maxFeePercentage) internal {
        ContractsCache memory contractsCache = ContractsCache(vaultManager, activePool, osdToken);
        LocalVariables_adjustVault memory vars;

        vars.price = priceFeed.fetchPrice();
        bool isRecoveryMode = _checkRecoveryMode(vars.price);

        if (_isDebtIncrease) {
            _requireValidMaxFeePercentage(_maxFeePercentage, isRecoveryMode);
            _requireNonZeroDebtChange(_OSDChange);
        }
        _requireSingularCollChange(_collWithdrawal);
        _requireNonZeroAdjustment(_collWithdrawal, _OSDChange);
        _requireVaultisActive(contractsCache.vaultManager, _borrower);

        // Confirm the operation is either a borrower adjusting their own vault, or a pure ROSE transfer from the Stability Pool to a vault
        assert(msg.sender == _borrower || (msg.sender == stabilityPoolAddress && msg.value > 0 && _OSDChange == 0));

        contractsCache.vaultManager.applyPendingRewards(_borrower);

        // Get the collChange based on whether or not ROSE was sent in the transaction
        (vars.collChange, vars.isCollIncrease) = _getCollChange(msg.value, _collWithdrawal);

        vars.netDebtChange = _OSDChange;

        // If the adjustment incorporates a debt increase and system is in Normal Mode, then trigger a borrowing fee
        if (_isDebtIncrease && !isRecoveryMode) { 
            vars.ROSEFee = _triggerBorrowingFee(contractsCache.vaultManager, _OSDChange, _maxFeePercentage, vars.price);
        }

        vars.debt = contractsCache.vaultManager.getVaultDebt(_borrower);
        vars.coll = contractsCache.vaultManager.getVaultColl(_borrower);
        
        // Get the vault's old ICR before the adjustment, and what its new ICR will be after the adjustment
        vars.oldICR = OrumMath._computeCR(vars.coll, vars.debt, vars.price);
        vars.newICR = _getNewICRFromVaultChange(vars.coll, vars.debt, vars.collChange, vars.isCollIncrease, vars.netDebtChange, _isDebtIncrease, vars.ROSEFee, vars.price);
        assert(_collWithdrawal <= vars.coll); 

        // Check the adjustment satisfies all conditions for the current system mode
        _requireValidAdjustmentInCurrentMode(isRecoveryMode, _collWithdrawal, _isDebtIncrease, vars);
            
        // When the adjustment is a debt repayment, check it's a valid amount and that the caller has enough OSD
        if (!_isDebtIncrease && _OSDChange > 0) {
            _requireAtLeastMinNetDebt(_getNetDebt(vars.debt)- vars.netDebtChange);
            _requireValidOSDRepayment(vars.debt, vars.netDebtChange);
            _requireSufficientOSDBalance(contractsCache.osdToken, _borrower, vars.netDebtChange);
        }

        (vars.newColl, vars.newDebt) = _updateVaultFromAdjustment(contractsCache.vaultManager, _borrower, vars.collChange, vars.isCollIncrease, vars.netDebtChange, _isDebtIncrease, vars.ROSEFee);
        vars.stake = contractsCache.vaultManager.updateStakeAndTotalStakes(_borrower);

        // Re-insert vault in to the sorted list
        uint newNICR = _getNewNominalICRFromVaultChange(vars.coll, vars.debt, vars.collChange, vars.isCollIncrease, vars.netDebtChange, _isDebtIncrease, vars.ROSEFee);
        sortedVaults.reInsert(_borrower, newNICR, _upperHint, _lowerHint);

        emit VaultUpdated(_borrower, vars.newDebt, vars.newColl, vars.stake, uint8(BorrowerOperation.adjustVault));
        emit BorrowFeeInROSE(msg.sender, vars.ROSEFee);

        // Use the unmodified _OSDChange here, as we don't send the fee to the user
        _moveTokensAndROSEFromAdjustment(
            contractsCache.activePool,
            contractsCache.osdToken,
            msg.sender,
            vars.collChange,
            vars.isCollIncrease,
            _OSDChange,
            _isDebtIncrease,
            vars.netDebtChange,
            vars.ROSEFee
        );

    }

    function closeVault() external override {
        IVaultManager vaultManagerCached = vaultManager;
        IActivePool activePoolCached = activePool;
        IOSDToken osdTokenCached = osdToken;

        _requireVaultisActive(vaultManagerCached, msg.sender);
        uint price = priceFeed.fetchPrice();
        _requireNotInRecoveryMode(price);

        vaultManagerCached.applyPendingRewards(msg.sender);

        uint coll = vaultManagerCached.getVaultColl(msg.sender);
        uint debt = vaultManagerCached.getVaultDebt(msg.sender);

        _requireSufficientOSDBalance(osdTokenCached, msg.sender, debt - OSD_GAS_COMPENSATION);

        uint newTCR = _getNewTCRFromVaultChange(coll, false, debt, false, 0, price);
        _requireNewTCRisAboveCCR(newTCR);

        vaultManagerCached.removeStake(msg.sender);
        vaultManagerCached.closeVault(msg.sender);

        emit VaultUpdated(msg.sender, 0, 0, 0, uint8(BorrowerOperation.closeVault));

        // Burn the repaid OSD from the user's balance and the gas compensation from the Gas Pool
        _repayOSD(activePoolCached, osdTokenCached, msg.sender, debt - OSD_GAS_COMPENSATION);
        _repayOSD(activePoolCached, osdTokenCached, gasPoolAddress, OSD_GAS_COMPENSATION);

        // Send the collateral back to the user
        activePoolCached.sendROSE(msg.sender, coll);
    }

    /**
     * Claim remaining collateral from a redemption or from a liquidation with ICR > MCR in Recovery Mode
     */
    function claimCollateral() external override {
        // send ROSE from CollSurplus Pool to owner
        collSurplusPool.claimColl(msg.sender);
    }

    // --- Helper functions ---

    function _triggerBorrowingFee(IVaultManager _vaultManager, uint _OSDAmount, uint _maxFeePercentage, uint _price) internal returns (uint) {
        _vaultManager.decayBaseRateFromBorrowing(); // decay the baseRate state variable
        uint OSDFee = _vaultManager.getBorrowingFee(_OSDAmount);

        _requireUserAcceptsFee(OSDFee, _OSDAmount, _maxFeePercentage);
        
        // Send fee to LQTY staking contract
        uint ROSEFee = (OSDFee * DECIMAL_PRECISION)/ _price;
        return ROSEFee;
    }

    function _getUSDValue(uint _coll, uint _price) internal pure returns (uint) {
        uint usdValue = (_price * _coll) / DECIMAL_PRECISION;

        return usdValue;
    }

    function _getCollChange(
        uint _collReceived,
        uint _requestedCollWithdrawal
    )
        internal
        pure
        returns(uint collChange, bool isCollIncrease)
    {
        if (_collReceived != 0) {
            collChange = _collReceived;
            isCollIncrease = true;
        } else {
            collChange = _requestedCollWithdrawal;
        }
    }

    // Update vault's coll and debt based on whether they increase or decrease
    function _updateVaultFromAdjustment
    (
        IVaultManager _vaultManager,
        address _borrower,
        uint _collChange,
        bool _isCollIncrease,
        uint _debtChange,
        bool _isDebtIncrease,
        uint _borrowFee
    )
        internal
        returns (uint, uint)
    {
        uint newColl = (_isCollIncrease) ? _vaultManager.increaseVaultColl(_borrower, _collChange)
                                        : _vaultManager.decreaseVaultColl(_borrower, _collChange);
        newColl = (_isDebtIncrease) ? _vaultManager.decreaseVaultColl(_borrower, _borrowFee): newColl;
        uint newDebt = (_isDebtIncrease) ? _vaultManager.increaseVaultDebt(_borrower, _debtChange)
                                        : _vaultManager.decreaseVaultDebt(_borrower, _debtChange);

        return (newColl, newDebt);
    }

    function _moveTokensAndROSEFromAdjustment
    (
        IActivePool _activePool,
        IOSDToken _osdToken,
        address _borrower,
        uint _collChange,
        bool _isCollIncrease,
        uint _OSDChange,
        bool _isDebtIncrease,
        uint _netDebtChange,
        uint _borrowFee
    )
        internal
    {
        if (_isDebtIncrease) {
            _withdrawOSD(_activePool, _osdToken, _borrower, _OSDChange, _netDebtChange);
            _activePool.sendROSE(orumFeeDistributionAddress, _borrowFee);
            
        } else {
            _repayOSD(_activePool, _osdToken, _borrower, _OSDChange);
        }

        if (_isCollIncrease) {
            _activePoolAddColl(_activePool, _collChange);
        } else {
            _activePool.sendROSE(_borrower, _collChange);
        }
    }

    // Send ROSE to Active Pool and increase its recorded ROSE balance
    function _activePoolAddColl(IActivePool _activePool, uint _amount) internal {
        (bool success, ) = address(_activePool).call{value: _amount}("");
        require(success, "BorrowerOps: Sending ROSE to ActivePool failed");
    }

    // Issue the specified amount of OSD to _account and increases the total active debt (_netDebtIncrease potentially includes a OSDFee)
    function _withdrawOSD(IActivePool _activePool, IOSDToken _osdToken, address _account, uint _OSDAmount, uint _netDebtIncrease) internal {
        _activePool.increaseOSDDebt(_netDebtIncrease);
        _osdToken.mint(_account, _OSDAmount);
    }

    // Burn the specified amount of OSD from _account and decreases the total active debt
    function _repayOSD(IActivePool _activePool, IOSDToken _osdToken, address _account, uint _OSD) internal {
        _activePool.decreaseOSDDebt(_OSD);
        _osdToken.burn(_account, _OSD);
    }

    // --- 'Require' wrapper functions ---

    function _requireSingularCollChange(uint _collWithdrawal) internal view {
        require(msg.value == 0 || _collWithdrawal == 0, "BorrowerOps: Cannot withdraw and add coll");
    }

    function _requireCallerIsBorrower(address _borrower) internal view {
        require(msg.sender == _borrower, "BorrowerOps: Caller must be the borrower for a withdrawal");
    }

    function _requireNonZeroAdjustment(uint _collWithdrawal, uint _OSDChange) internal view {
        require(msg.value != 0 || _collWithdrawal != 0 || _OSDChange != 0, "BorrowerOps: There must be either a collateral change or a debt change");
    }

    function _requireVaultisActive(IVaultManager _vaultManager, address _borrower) internal view {
        uint status = _vaultManager.getVaultStatus(_borrower);
        require(status == 1, "BorrowerOps: Vault does not exist or is closed");
    }

    function _requireVaultisNotActive(IVaultManager _vaultManager, address _borrower) internal view {
        uint status = _vaultManager.getVaultStatus(_borrower);
        require(status != 1, "BorrowerOps: Vault is active");
    }

    function _requireNonZeroDebtChange(uint _OSDChange) internal pure {
        require(_OSDChange > 0, "BorrowerOps: Debt increase requires non-zero debtChange");
    }
   
    function _requireNotInRecoveryMode(uint _price) internal view {
        require(!_checkRecoveryMode(_price), "BorrowerOps: Operation not permitted during Recovery Mode");
    }

    function _requireNoCollWithdrawal(uint _collWithdrawal) internal pure {
        require(_collWithdrawal == 0, "BorrowerOps: Collateral withdrawal not permitted Recovery Mode");
    }

    function _requireValidAdjustmentInCurrentMode 
    (
        bool _isRecoveryMode,
        uint _collWithdrawal,
        bool _isDebtIncrease, 
        LocalVariables_adjustVault memory _vars
    ) 
        internal 
        view 
    {
        /* 
        *In Recovery Mode, only allow:
        *
        * - Pure collateral top-up
        * - Pure debt repayment
        * - Collateral top-up with debt repayment
        * - A debt increase combined with a collateral top-up which makes the ICR >= 150% and improves the ICR (and by extension improves the TCR).
        *
        * In Normal Mode, ensure:
        *
        * - The new ICR is above MCR
        * - The adjustment won't pull the TCR below CCR
        */
        if (_isRecoveryMode) {
            _requireNoCollWithdrawal(_collWithdrawal);
            if (_isDebtIncrease) {
                _requireICRisAboveCCR(_vars.newICR);
                _requireNewICRisAboveOldICR(_vars.newICR, _vars.oldICR);
            }       
        } else { // if Normal Mode
            _requireICRisAboveMCR(_vars.newICR);
            _vars.newTCR = _getNewTCRFromVaultChange(_vars.collChange, _vars.isCollIncrease, _vars.netDebtChange, _isDebtIncrease, _vars.ROSEFee, _vars.price);
            _requireNewTCRisAboveCCR(_vars.newTCR);  
        }
    }

    function _requireICRisAboveMCR(uint _newICR) internal view {
        require(_newICR >= MCR, "BorrowerOps: An operation that would result in ICR < MCR is not permitted");
    }

    function _requireICRisAboveCCR(uint _newICR) internal view {
        require(_newICR >= CCR, "BorrowerOps: Operation must leave vault with ICR >= CCR");
    }

    function _requireNewICRisAboveOldICR(uint _newICR, uint _oldICR) internal pure {
        require(_newICR >= _oldICR, "BorrowerOps: Cannot decrease your Vault's ICR in Recovery Mode");
    }

    function _requireNewTCRisAboveCCR(uint _newTCR) internal view {
        require(_newTCR >= CCR, "BorrowerOps: An operation that would result in TCR < CCR is not permitted");
    }

    function _requireAtLeastMinNetDebt(uint _netDebt) internal view {
        require (_netDebt >= MIN_NET_DEBT, "BorrowerOps: Vault's net debt must be greater than minimum");
    }

    function _requireValidOSDRepayment(uint _currentDebt, uint _debtRepayment) internal view {
        require(_debtRepayment <= _currentDebt - OSD_GAS_COMPENSATION, "BorrowerOps: Amount repaid must not be larger than the Vault's debt");
    }

    function _requireCallerIsStabilityPool() internal view {
        require(msg.sender == stabilityPoolAddress, "BorrowerOps: Caller is not Stability Pool");
    }

     function _requireSufficientOSDBalance(IOSDToken _osdToken, address _borrower, uint _debtRepayment) internal view {
        require(_osdToken.balanceOf(_borrower) >= _debtRepayment, "BorrowerOps: Caller doesnt have enough OSD to make repayment");
    }

    function _requireValidMaxFeePercentage(uint _maxFeePercentage, bool _isRecoveryMode) internal view {
        if (_isRecoveryMode) {
            require(_maxFeePercentage <= DECIMAL_PRECISION,
                "Max fee percentage must less than or equal to 100%");
        } else {
            require(_maxFeePercentage >= BORROWING_FEE_FLOOR && _maxFeePercentage <= DECIMAL_PRECISION,
                "Max fee percentage must be between 0.5% and 100%");
        }
    }

    // --- ICR and TCR getters ---

    // Compute the new collateral ratio, considering the change in coll and debt. Assumes 0 pending rewards.
    function _getNewNominalICRFromVaultChange
    (
        uint _coll,
        uint _debt,
        uint _collChange,
        bool _isCollIncrease,
        uint _debtChange,
        bool _isDebtIncrease,
        uint _borrowFee
    )
        pure
        internal
        returns (uint)
    {
        (uint newColl, uint newDebt) = _getNewVaultAmounts(_coll, _debt, _collChange, _isCollIncrease, _debtChange, _isDebtIncrease, _borrowFee);

        uint newNICR = OrumMath._computeNominalCR(newColl, newDebt);
        return newNICR;
    }

    // Compute the new collateral ratio, considering the change in coll and debt. Assumes 0 pending rewards.
    function _getNewICRFromVaultChange
    (
        uint _coll,
        uint _debt,
        uint _collChange,
        bool _isCollIncrease,
        uint _debtChange,
        bool _isDebtIncrease,
        uint _borrowFee,
        uint _price
    )
        pure
        internal
        returns (uint)
    {
        (uint newColl, uint newDebt) = _getNewVaultAmounts(_coll, _debt, _collChange, _isCollIncrease, _debtChange, _isDebtIncrease, _borrowFee);

        uint newICR = OrumMath._computeCR(newColl, newDebt, _price);
        return newICR;
    }

    function _getNewVaultAmounts(
        uint _coll,
        uint _debt,
        uint _collChange,
        bool _isCollIncrease,
        uint _debtChange,
        bool _isDebtIncrease,
        uint _borrowFee
    )
        internal
        pure
        returns (uint, uint)
    {
        uint newColl = _coll;
        uint newDebt = _debt;

        newColl = _isCollIncrease ? _coll +_collChange:  _coll - _collChange;
        newDebt = _isDebtIncrease ? _debt + _debtChange : _debt - _debtChange;
        newColl = _isDebtIncrease ? newColl - _borrowFee: newColl;

        return (newColl, newDebt);
    }

    function _getNewTCRFromVaultChange
    (
        uint _collChange,
        bool _isCollIncrease,
        uint _debtChange,
        bool _isDebtIncrease,
        uint _borrowFee,
        uint _price
    )
        internal
        view
        returns (uint)
    {
        uint totalColl = getEntireSystemColl();
        uint totalDebt = getEntireSystemDebt();

        totalColl = _isCollIncrease ? totalColl + _collChange : totalColl - _collChange;
        totalDebt = _isDebtIncrease ? totalDebt + _debtChange: totalDebt - _debtChange;
        totalColl = _isDebtIncrease ? totalColl - _borrowFee: totalColl;

        uint newTCR = OrumMath._computeCR(totalColl, totalDebt, _price);
        return newTCR;
    }

    function getCompositeDebt(uint _debt) external view override returns (uint) {
        return _getCompositeDebt(_debt);
    }

    function changeTreasuryAddress(address _orumFeeDistributionAddress) external onlyOwner{
        // checkContract(_orumFeeDistributionAddress);
        orumFeeDistributionAddress = _orumFeeDistributionAddress;
        emit OrumRevenueAddressChanged(_orumFeeDistributionAddress);
    }
    function changeBorrowFeeFloor(uint _newBorrowFeeFloor) external onlyOwner{
        BORROWING_FEE_FLOOR = DECIMAL_PRECISION / 1000 * _newBorrowFeeFloor;
    }
    function changeMCR(uint _newMCR) external onlyOwner{
        MCR = _newMCR;
    }
    function changeCCR(uint _newCCR) external onlyOwner{
        CCR = _newCCR;
    }
    function changeMinNetDebt(uint _newMinDebt) external onlyOwner{
        MIN_NET_DEBT = _newMinDebt;
    }
    function changeGasCompensation(uint _OSDGasCompensation) external onlyOwner{
        OSD_GAS_COMPENSATION = _OSDGasCompensation;
    }
}

