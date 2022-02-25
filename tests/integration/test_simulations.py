from re import A
from brownie import Wei, chain

def test_liquidate(isolation, alice, owner, bob, charlie, katy, lauren, eren, BorrowerOps, VaultManager, StabilityPool, MockV3Aggregator):
    ######################### Description ########################
    ### Open 6 vaults, push 4 of them into liquidation zone,   ###
    ### call liquidate on an intermediate vault by address,    ###
    ### and then call VaultManager.liquidateVaults(4) and check###
    ### if a healthy vault is also being liquidated along with ###
    ### the remaining 3 risky vaults                           ###
    ##############################################################

    # vault data
    address_hint = '0x'+'0'*40
    eren_debt, eren_coll = Wei(15000e18), Wei('10 ether')
    alice_debt, alice_coll = Wei(100e18), Wei('1 ether')
    bob_debt, bob_coll = Wei(2500e18), Wei('1 ether')
    charlie_debt, charlie_coll = Wei(2500e18), Wei('1 ether')
    katy_debt, katy_coll = Wei(2500e18), Wei('1 ether')
    lauren_debt, lauren_coll = Wei(2500e18), Wei('1 ether')
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    # open 6 vaults
    borrower_ops.openVault(Wei(1e18), eren_debt, address_hint, address_hint, {"from": eren, "value": eren_coll})
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    borrower_ops.openVault(Wei(1e18), katy_debt, address_hint, address_hint, {"from": katy, "value": katy_coll})
    borrower_ops.openVault(Wei(1e18), lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # eren deposits some OSD into the stability pool
    stability_pool.provideToSP(Wei(10000e18), {"from": eren})
    # push the last 4 vaults into liquidation zone by manually lowering the ETH/USD price
    mock_aggregator.updateAnswer(Wei(3000e18))
    # liquidate charlie by his address
    vault_manager.liquidate(charlie.address, {"from": eren})
    # check the status of charlie's vault
    assert vault_manager.Vaults(charlie.address)[3] == 3
    # now liquidate the last 4 vaults 
    vault_manager.liquidateVaults(4, {"from": eren})
    # check whether only 3 vaults are getting liquidated and the last one is skipped
    assert vault_manager.Vaults(lauren.address)[3] == 3 and vault_manager.Vaults(katy.address)[3] == 3 and vault_manager.Vaults(bob.address)[3] == 3 and vault_manager.Vaults(eren.address)[3] == 1 and vault_manager.Vaults(alice.address)[3] == 1

def test_redemptions_change_borrow_fees(isolation, users, BorrowerOps, VaultManager, OSDToken, HintHelpers, SortedVaults, PriceFeed):
    ######################### Description #########################
    ### Check if succesive redemptions have any effect on the borrow fee ###
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    osd_token = OSDToken[-1]
    hint_helpers = HintHelpers[-1]
    sorted_vaults = SortedVaults[-1]
    price_feed = PriceFeed[-1]
    address_hint = '0x'+'0'*40

    # get the borrowing fee for 1000OSD
    init_borrow_fee = vault_manager.getBorrowingFee(Wei(1000e18))
    price = price_feed.fetchPrice()
    # open 20 vaults
    for i in range(20):
        borrower_ops.openVault(Wei(1e18), Wei(2100e18), address_hint, address_hint, {"from": users[i], "value": Wei('1 ether')})
    # send OSD to some 20 users
    for i in range(20):
        osd_token.transfer(users[i+20], Wei(1000e18), {"from": users[i]})
    # redeem 1000 OSD for equal worth of ROSE
    hints = get_redemption_hints(Wei(1000e18),price, sorted_vaults, hint_helpers)
    for i in range(20):
        vault_manager.redeemCollateral(Wei(1000e18), hints[0], hints[1], hints[2], hints[3], Wei(0), Wei(1e18), {"from": users[i+20]})
    curr_borrow_fee = vault_manager.getBorrowingFee(Wei(1000e18))

    assert curr_borrow_fee > init_borrow_fee
    

def get_redemption_hints(amount, price, sorted_vaults, hint_helpers):
    # get the current conversion price
    (first_redemption_hint, partial_redemption_new_ICR, truncated_osd) = hint_helpers.getRedemptionHints(amount, price, 5)
    approx_partial_redemption_hint = hint_helpers.getApproxHint(partial_redemption_new_ICR, 5, 42)
    exact_partial_redemption_hint = sorted_vaults.findInsertPosition(partial_redemption_new_ICR, approx_partial_redemption_hint[0], approx_partial_redemption_hint[0])

    return (first_redemption_hint, exact_partial_redemption_hint[0], exact_partial_redemption_hint[1], partial_redemption_new_ICR)




