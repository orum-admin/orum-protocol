from brownie import BorrowerOps, VaultManager, OSDToken, OrumFeeDistribution, HintHelpers, PriceFeed, SortedVaults
from brownie import Wei, chain
from scripts.utils.helpful_scripts import get_accounts

def test_redeem_collateral(deploy, owner):
    # get test accounts
    # first 5 accounts to open vaults, 6th account redeems ROSE
    accounts = get_accounts(6)
    # get the contracts
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    osd_token = OSDToken[-1]
    orum_fee_distribution = OrumFeeDistribution[-1]
    # collateral deposited and debt withdrawn by the 5 accounts
    collateral_amounts = ['1 ether','1 ether','1 ether','1 ether','1 ether']
    debt_amounts = ['600 ether','500 ether','600 ether','700 ether','580 ether']
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei('1 ether')

    ### Opening vaults ###
    for idx, (coll, debt) in enumerate(zip(collateral_amounts,debt_amounts)):
        borrower_ops.openVault(maxFeePercentage, Wei(debt), address_hint, address_hint, {"from": accounts[idx], "value": Wei(coll)})
    ### send 500 OSD from accounts[1] to accounts[5]
    osd_token.transfer(accounts[5].address, Wei(30e18), {"from": accounts[4]})
    # move 14 days into the future to start receiving revenue in the OrumFeeDistribution
    chain.mine(timedelta=14*86400)
    vault_manager.changeTreasuryAddress(orum_fee_distribution.address, {"from": owner})
    ### get the ROSE balance of treasury and orum staking before redemption
    orum_fee_distribution_balance_init = orum_fee_distribution.balance()
    assert orum_fee_distribution_balance_init == 0
    ### get redemption hints
    redeem_amount = Wei('30 ether')
    hints = get_redemption_hints(redeem_amount)
    ### Redeem 500 OSD for ROSE with accounts[5]
    tx = vault_manager.redeemCollateral(redeem_amount, hints[0], hints[1], hints[2], hints[3], Wei(0), maxFeePercentage, {"from": accounts[4]})
    # get the ROSE balance of treasury and orum staking after redemption
    orum_fee_distribution_balance_curr = orum_fee_distribution.balance()
    fee = tx.events['Redemption']['_ROSEFee'] 
    assert orum_fee_distribution_balance_curr == fee

def get_redemption_hints(amount):
    # get the current conversion price
    price = PriceFeed[-1].fetchPrice()
    hint_helpers = HintHelpers[-1]
    (first_redemption_hint, partial_redemption_new_ICR, truncated_osd) = hint_helpers.getRedemptionHints(amount, price, 5)
    approx_partial_redemption_hint = hint_helpers.getApproxHint(partial_redemption_new_ICR, 5, 42)
    exact_partial_redemption_hint = SortedVaults[-1].findInsertPosition(partial_redemption_new_ICR, approx_partial_redemption_hint[0], approx_partial_redemption_hint[0])

    return (first_redemption_hint, exact_partial_redemption_hint[0], exact_partial_redemption_hint[1], partial_redemption_new_ICR)







