from brownie import Wei

def test_orum_token_farming(deploy, isolation, alice, bob, charlie, katy, lauren, BorrowerOps, OSDToken, StabilityPool, OrumToken):
    # vault params 
    address_hint = '0x' + '0'*40
    alice_debt = Wei(2000e18)
    bob_debt = Wei(1900e18)
    charlie_debt = Wei(200e18)
    lauren_debt = Wei(3000e18)
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_token = OrumToken[-1]
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(11e17)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e17)})
    # transfer some osd to katy
    osd_token.transfer(katy, Wei(250), {"from": bob})
    # provide osd to the stability pool
    stability_pool.provideToSP(Wei(250), {"from": katy})
    # make some spam transaction to pass some time 
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": lauren, "value": Wei(3e18)})
    borrower_ops.withdrawOSD(Wei(1e18), Wei(300e18), address_hint, address_hint, {"from": lauren})
    # check katy's Orum balance
    assert orum_token.balanceOf(katy) > 0
