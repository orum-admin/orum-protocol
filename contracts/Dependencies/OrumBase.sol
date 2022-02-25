// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import "./OrumMath.sol";
import "../interfaces/IActivePool.sol";
import "../interfaces/IDefaultPool.sol";
import "../interfaces/IPriceFeed.sol";
import "../interfaces/IOrumBase.sol";


/* 
* Base contract for VaultManager, BorrowerOps and StabilityPool. Contains global system constants and
* common functions. 
*/
contract OrumBase is IOrumBase {
    using SafeMath for uint;

    uint constant public DECIMAL_PRECISION = 1e18;

    uint constant public _100pct = 1000000000000000000; // 1e18 == 100%

    // Minimum collateral ratio for individual Vaults
    uint public MCR = 1350000000000000000; // 135%;

    // Critical system collateral ratio. If the system's total collateral ratio (TCR) falls below the CCR, Recovery Mode is triggered.
    uint public CCR = 1750000000000000000; // 175%

    // Amount of OSD to be locked in gas pool on opening vaults
    uint public OSD_GAS_COMPENSATION = 10e18;

    // Minimum amount of net OSD debt a vault must have
    uint public MIN_NET_DEBT = 50e18;

    uint public PERCENT_DIVISOR = 200; // dividing by 200 yields 0.5%

    uint public BORROWING_FEE_FLOOR = DECIMAL_PRECISION / 10000 * 75 ; // 0.75%

    uint public TREASURY_LIQUIDATION_PROFIT = DECIMAL_PRECISION / 100 * 20; // 20%
    


    address public contractOwner;

    IActivePool public activePool;

    IDefaultPool public defaultPool;

    IPriceFeed public override priceFeed;

    constructor() {
        contractOwner = msg.sender;
    }
    // --- Gas compensation functions ---

    // Returns the composite debt (drawn debt + gas compensation) of a vault, for the purpose of ICR calculation
    function _getCompositeDebt(uint _debt) internal view  returns (uint) {
        return _debt.add(OSD_GAS_COMPENSATION);
    }
    function _getNetDebt(uint _debt) internal view returns (uint) {
        return _debt.sub(OSD_GAS_COMPENSATION);
    }
    // Return the amount of ROSE to be drawn from a vault's collateral and sent as gas compensation.
    function _getCollGasCompensation(uint _entireColl) internal view returns (uint) {
        return _entireColl / PERCENT_DIVISOR;
    }
    // // change system base values
    // function changeMCR(uint _newMCR) external {
    //     _requireCallerIsOwner();
    //     MCR = _newMCR;
    // }
    // function changeCCR(uint _newCCR) external {
    //     _requireCallerIsOwner();
    //     CCR = _newCCR;
    // }
    // function changeLiquidationReward(uint8 _PERCENT_DIVISOR) external {
    //     _requireCallerIsOwner();
    //     PERCENT_DIVISOR = _PERCENT_DIVISOR;
    // }
    // function changeTreasuryFeeShare(uint8 _percent) external {
    //     _requireCallerIsOwner();
    //     TREASURY_FEE_DIVISOR = DECIMAL_PRECISION / 100 * _percent;
    // }
    // function changeSPLiquidationProfit(uint8 _percent) external {
    //     _requireCallerIsOwner();
    //     STABILITY_POOL_LIQUIDATION_PROFIT = DECIMAL_PRECISION / 100 * _percent;
    // }
    // function changeBorrowingFee(uint8 _newBorrowFee) external {
    //     _requireCallerIsOwner();
    //     BORROWING_FEE_FLOOR = DECIMAL_PRECISION / 1000 * _newBorrowFee;
    // }
    // function changeMinNetDebt(uint _newMinDebt) external {
    //     _requireCallerIsOwner();
    //     MIN_NET_DEBT = _newMinDebt;
    // }
    // function changeGasCompensation(uint _OSDGasCompensation) external {
    //     _requireCallerIsOwner();
    //     OSD_GAS_COMPENSATION = _OSDGasCompensation;
    // }
    function getEntireSystemColl() public view returns (uint entireSystemColl) {
        uint activeColl = activePool.getROSE();
        uint liquidatedColl = defaultPool.getROSE();

        return activeColl.add(liquidatedColl);
    }

    function getEntireSystemDebt() public view returns (uint entireSystemDebt) {
        uint activeDebt = activePool.getOSDDebt();
        uint closedDebt = defaultPool.getOSDDebt();

        return activeDebt.add(closedDebt);
    }
    function _getTreasuryLiquidationProfit(uint _amount) internal view returns (uint){
        return _amount.mul(TREASURY_LIQUIDATION_PROFIT).div(DECIMAL_PRECISION);
    }
    function _getTCR(uint _price) internal view returns (uint TCR) {
        uint entireSystemColl = getEntireSystemColl();
        uint entireSystemDebt = getEntireSystemDebt();

        TCR = OrumMath._computeCR(entireSystemColl, entireSystemDebt, _price);
        return TCR;
    }

    function _checkRecoveryMode(uint _price) internal view returns (bool) {
        uint TCR = _getTCR(_price);

        return TCR < CCR;
    }

    function _requireUserAcceptsFee(uint _fee, uint _amount, uint _maxFeePercentage) internal pure {
        uint feePercentage = _fee.mul(DECIMAL_PRECISION).div(_amount);
        require(feePercentage <= _maxFeePercentage, "Fee exceeded provided maximum");
    }

    function _requireCallerIsOwner() internal view {
        require(msg.sender == contractOwner, "OrumBase: caller not owner");
    }

    function changeOwnership(address _newOwner) external {
        require(msg.sender == contractOwner, "OrumBase: Caller not owner");
        contractOwner = _newOwner;
    }

}