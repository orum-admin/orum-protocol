// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import "./SafeMath.sol";

// Based on Liquity's OrumMath library: https://github.com/liquity/dev/blob/main/packages/contracts/contracts/Dependencies/OrumMath.sol

library OrumMath {
    using SafeMath for uint;

    uint internal constant DECIMAL_PRECISION = 1e18;

    /* Precision for Nominal ICR (independent of price). Rationale for the value:
    *
    * - Making it "too high" could lead to overflows.
    * - Making it "too low" could lead to an ICR equal to zero, due to truncation from Solidity floor division.
    *
    * This value of 1e20 is chosen for safety: the NICR will only overflow for numerator > ~1e39 ROSE,
    * and will only truncate to 0 if the denominator is at least 1e20 times greater than the numerator.
    *
    */

    uint internal constant NICR_PRECISION = 1e20;

    function _min(uint _a, uint _b) internal pure returns (uint) {
        return (_a < _b) ? _a : _b;
    }
    function _max(int _a, int _b) internal pure returns (uint) {
        return (_a >= _b) ? uint(_a) : uint(_b);
    }

    /*
    * Multiply two decimal numbers and use normal rounding rules
    * - round product up if 19'th mantissa digit >= 5
    * - round product down if 19'th mantissa digit < 5
    * 
    * Used only inside exponentiation, _decPow().
    */

    function decMul(uint x, uint y) internal pure returns (uint decProd) {
        uint prod_xy = x.mul(y);
        decProd = prod_xy.add(DECIMAL_PRECISION/2).div(DECIMAL_PRECISION);
    }
    
    function _decPow(uint _base, uint _minutes) internal pure returns (uint) {
       
        if (_minutes > 525600000) {_minutes = 525600000;}  // cap to avoid overflow
    
        if (_minutes == 0) {return DECIMAL_PRECISION;}

        uint y = DECIMAL_PRECISION;
        uint x = _base;
        uint n = _minutes;

        // Exponentiation-by-squaring
        while (n > 1) {
            if (n % 2 == 0) {
                x = decMul(x, x);
                n = n.div(2);
            } else { // if (n % 2 != 0)
                y = decMul(x, y);
                x = decMul(x, x);
                n = (n.sub(1)).div(2);
            }
        }

        return decMul(x, y);
  }

    function _getAbsoluteDifference(uint _a, uint _b) internal pure returns (uint) {
        return (_a >= _b) ? _a.sub(_b) : _b.sub(_a);
    }

    function _computeNominalCR(uint _coll, uint _debt) internal pure returns (uint) {
        if (_debt > 0) {
            return _coll.mul(NICR_PRECISION).div(_debt);
        }
        // Return the maximal value for uint256 if the Vault has a debt of 0. Represents "infinite" CR.
        else { // if (_debt == 0)
            return 2**256 - 1;
        }
    }

    function _computeCR(uint _coll, uint _debt, uint _price) internal pure returns (uint) {
        if (_debt > 0) {
            uint newCollRatio = _coll.mul(_price).div(_debt);

            return newCollRatio;
        }
        // Return the maximal value for uint256 if the Vault has a debt of 0. Represents "infinite" CR.
        else { // if (_debt == 0)
            return 2**256 - 1; 
        }
    }
}
