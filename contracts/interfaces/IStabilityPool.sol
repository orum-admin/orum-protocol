// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

/*
 * The Stability Pool holds OSD tokens deposited by Stability Pool depositors.
 *
 * When a Vault is liquidated, then depending on system conditions, some of its OSD debt gets offset with
 * OSD in the Stability Pool:  that is, the offset debt evaporates, and an equal amount of OSD tokens in the Stability Pool is burned.
 *
 * Thus, a liquidation causes each depositor to receive a OSD loss, in proportion to their deposit as a share of total deposits.
 * They also receive an ROSE gain, as the ROSE collateral of the liquidated Vault is distributed among Stability depositors,
 * in the same proportion.
 *
 * When a liquidation occurs, it depletes every deposit by the same fraction: for example, a liquidation that depletes 40%
 * of the total OSD in the Stability Pool, depletes 40% of each deposit.
 *
 * A deposit that has experienced a series of liquidations is termed a "compounded deposit": each liquidation depletes the deposit,
 * multiplying it by some factor in range ]0,1[
 *
 * Please see the implementation spec in the proof document, which closely follows on from the compounded deposit / ROSE gain derivations:
 * https://github.com/liquity/liquity/blob/master/papers/Scalable_Reward_Distribution_with_Compounding_Stakes.pdf
 */
interface IStabilityPool {

    // --- Events ---
    
    event StabilityPoolROSEBalanceUpdated(uint _newBalance);
    event StabilityPoolOSDBalanceUpdated(uint _newBalance);

    event BorrowerOpsAddressChanged(address _newBorrowerOpsAddress);
    event VaultManagerAddressChanged(address _newVaultManagerAddress);
    event ActivePoolAddressChanged(address _newActivePoolAddress);
    event DefaultPoolAddressChanged(address _newDefaultPoolAddress);
    event OSDTokenAddressChanged(address _newOSDTokenAddress);
    event SortedVaultsAddressChanged(address _newSortedVaultsAddress);
    event PriceFeedAddressChanged(address _newPriceFeedAddress);
    event CommunityIssuanceAddressChanged(address _newCommunityIssuanceAddress);

    event P_Updated(uint _P);
    event S_Updated(uint _S, uint128 _epoch, uint128 _scale);
    event G_Updated(uint _G, uint128 _epoch, uint128 _scale);
    event EpochUpdated(uint128 _currentEpoch);
    event ScaleUpdated(uint128 _currentScale);

    event DepositSnapshotUpdated(address indexed _depositor, uint _P, uint _S, uint _G);
    event UserDepositChanged(address indexed _depositor, uint _newDeposit);

    event ROSEGainWithdrawn(address indexed _depositor, uint _ROSE, uint _OSDLoss);
    event OrumPaidToDepositor(address indexed _depositor, uint _orum);
    event RoseSent(address _to, uint _amount);

    // --- Functions ---

    /*
     * Called only once on init, to set addresses of other Liquity contracts
     * Callable only by owner, renounces ownership at the end
     */
    function setAddresses(
        address _borrowerOpsAddress,
        address _VaultManagerAddress,
        address _activePoolAddress,
        address _osdTokenAddress,
        address _sortedVaultsAddress,
        address _priceFeedAddress,
        address _communityIssuanceAddress
    ) external;

    function provideToSP(uint _amount) external;

    function withdrawFromSP(uint _amount) external;

    function withdrawROSEGainToVault(address _upperHint, address _lowerHint) external;

    function offset(uint _debt, uint _coll) external;

    function getROSE() external view returns (uint);

    function getTotalOSDDeposits() external view returns (uint);

    function getDepositorROSEGain(address _depositor) external view returns (uint);

    function getDepositorOrumGain(address _depositor) external view returns (uint);

    function getCompoundedOSDDeposit(address _depositor) external view returns (uint);

    /*
     * Fallback function
     * Only callable by Active Pool, it just accounts for ROSE received
     * receive() external payable;
     */
}