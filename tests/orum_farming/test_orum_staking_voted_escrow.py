from datetime import timedelta
from distutils.command import check
from brownie import Wei, chain

def test_orum_farming(alice, bob, charlie, katy, lauren, isolation, BorrowerOps, StabilityPool, OSDToken, OrumToken):
    # Data parameters
    address_hint = '0x'+'0'*40
    alice_debt = Wei(100000e18)
    bob_debt = Wei(90000e18)
    charlie_debt = Wei(100000e18)
    # get the latest depoloyed contracts
    borrower_ops = BorrowerOps[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_token = OrumToken[-1]
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei('70 ether')})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei('50 ether')})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei('50 ether')})
    # send some osd tokens to katy and lauren
    osd_token.transfer(katy, Wei(50000e18), {"from": alice})
    osd_token.transfer(lauren, Wei(39000e18), {"from": bob})
    # Orum balance of katy and lauren
    orum_katy_init_balance, orum_lauren_init_balance = orum_token.balanceOf(katy), orum_token.balanceOf(lauren)
    # The balance should initially be zero
    check_true = orum_katy_init_balance == 0 and orum_lauren_init_balance == 0
    # deposit osd tokens into the stability pool contract
    stability_pool.provideToSP(Wei(50000e18), {"from": katy})
    stability_pool.provideToSP(Wei(30000e18), {"from": lauren})
    # move forward in time to accumulate (farm) Orum tokens
    chain.mine(timedelta=7*24*60*60)
    # withdraw osd tokens from stability pool to trigger Orum gains
    stability_pool.withdrawFromSP(Wei(20000e18), {"from": katy})
    stability_pool.withdrawFromSP(Wei(15000e18), {"from": lauren})
    # check the Orum balance of both katy and lauren
    # It should have increased due to farming
    orum_katy_curr_balance, orum_lauren_curr_balance = orum_token.balanceOf(katy), orum_token.balanceOf(lauren)
    check_true = check_true and orum_lauren_init_balance != orum_lauren_curr_balance and orum_katy_init_balance != orum_katy_curr_balance
    assert check_true == True

def test_orum_farming_fees(alice, bob, charlie, katy, lauren, isolation, BorrowerOps, StabilityPool, OSDToken, OrumToken, OrumFeeDistribution, VotedEscrow):
    # Data parameters
    address_hint = '0x'+'0'*40
    alice_debt = Wei(100000e18)
    bob_debt = Wei(90000e18)
    charlie_debt = Wei(100000e18)
    # get the latest depoloyed contracts
    borrower_ops = BorrowerOps[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_token = OrumToken[-1]
    orum_revenue = OrumFeeDistribution[-1]
    voted_escrow = VotedEscrow[-1]
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei('70 ether')})
    # orum_revenue.checkpoint_token()
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei('50 ether')})
    # orum_revenue.checkpoint_token()
    # send some osd tokens to katy and lauren
    osd_token.transfer(katy, Wei(50000e18), {"from": alice})
    osd_token.transfer(lauren, Wei(39000e18), {"from": bob})
    # deposit osd tokens into the stability pool contract
    stability_pool.provideToSP(Wei(30000e18), {"from": katy})
    stability_pool.provideToSP(Wei(30000e18), {"from": lauren})
    # move forward in time to accumulate (farm) Orum tokens
    chain.mine(timedelta= 7*24*60*60)
    # withdraw osd tokens from stability pool to trigger Orum gains
    stability_pool.withdrawFromSP(Wei(20000e18), {"from": katy})
    stability_pool.withdrawFromSP(Wei(20000e18), {"from": lauren})
    katy_init_balance = katy.balance
    # check the Orum balance of both katy and lauren
    # It should have increased due to farming
    orum_katy_curr_balance, orum_lauren_curr_balance = orum_token.balanceOf(katy), orum_token.balanceOf(lauren)
    # check_true = check_true and orum_lauren_init_balance != orum_lauren_curr_balance and orum_katy_init_balance != orum_katy_curr_balance
    # set allowance of orum tokens of katy and lauren to orumRevenue contract 
    orum_token.approve(voted_escrow.address, orum_katy_curr_balance, {"from": katy})
    orum_token.approve(voted_escrow.address, orum_lauren_curr_balance, {"from": lauren})
    # chain.mine(timedelta = 14 * 86400)
    # stake orum tokens into the voted escrow contract
    voted_escrow.create_lock(orum_katy_curr_balance, 365 * 86400 , {"from": katy})
    chain.mine(timedelta=14*24*60*60)
    voted_escrow.create_lock(orum_lauren_curr_balance, 365 * 86400, {"from": lauren})
    # chain.mine(timedelta=14*24*60*60)
    # borrower_ops.openVault(Wei(1e18), 10e18 , address_hint, address_hint, {"from": charlie, "value": Wei('50 ether')})
    # chain.mine(timedelta = 14 * 86400)
    # # get katy's nft token ID
    # katy_nft_token_ID = voted_escrow.tokenOfOwnerByIndex(katy,0)
    # orum_revenue.checkpoint_token()
    # orum_revenue.claim(0, {"from": katy})

# 100039062047892964203

# 100042642103885690305
    # borrower_ops.withdrawOSD(Wei(1e18), Wei(2000e18), address_hint, address_hint, {"from": charlie})
    # orum_revenue.checkpoint_token()
    # chain.mine(timedelta = 14 * 86400)
    # orum_revenue.checkpointToken()
    # katy_claimable_reward = orum_revenue.claim(katy.address) # 
    assert False

def test_ser(isolation, alice, bob, charlie, ash, katy, OrumToken, VotedEscrow, OrumFeeDistribution, BorrowerOps):
    # get the latest deployed contracts
    voted_escrow = VotedEscrow[-1]
    orum_revenue = OrumFeeDistribution[-1]
    borrower_ops = BorrowerOps[-1]
    orum_token = OrumToken[-1]

    orum_token.approve(voted_escrow.address, orum_token.balanceOf(alice), {"from": alice})
    orum_token.approve(voted_escrow.address, orum_token.balanceOf(bob), {"from": bob})
    orum_token.approve(voted_escrow.address, orum_token.balanceOf(charlie), {"from": charlie})
    orum_token.approve(voted_escrow.address, orum_token.balanceOf(ash), {"from": ash})

    voted_escrow.create_lock(orum_token.balanceOf(alice), 365 * 86400 , {"from": alice})
    voted_escrow.create_lock(orum_token.balanceOf(bob), 365 * 86400 , {"from": bob})
    voted_escrow.create_lock(orum_token.balanceOf(charlie), 365 * 86400 , {"from": charlie})

    chain.mine(timedelta = 14 * 86400)

    orum_revenue.checkpoint_token()

    borrower_ops.openVault(Wei(1e18), 10e18 , '0x'+'0'*40, '0x'+'0'*40, {"from": katy, "value": Wei('50 ether')})
    borrower_ops.withdrawOSD(Wei(1e18), Wei(2000e18),  '0x'+'0'*40, '0x'+'0'*40, {"from": charlie})

    voted_escrow.create_lock(orum_token.balanceOf(ash), 365 * 86400 , {"from": ash})
    chain.mine(timedelta = 7 * 86400)

    orum_revenue.claim(0, {"from": alice})
    orum_revenue.claim(0, {"from": bob})
    orum_revenue.claim(0, {"from": charlie})
    orum_revenue.claim(0, {"from": ash})

    assert False



# brownie test tests/orum_farming/test_orum_staking_voted_escrow.py -k test_ser --network development --interactive

    



