from audioop import add
from brownie import Wei


def test_borrow_fee_equal_to_coll_decrease(isolation, BorrowerOps, VaultManager, alice):
    ### Description ###
    # Test to check whether the borrower's coll is decreased by the borrow fee of that operation
    # data
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei(1e18)
    alice_debt = Wei(1000e18)
    alice_coll = Wei('1 ether')
    # Get the latest depoyed contracts
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    # alice opens a vault and withdraws 1000 OSD
    tx = borrower_ops.openVault(maxFeePercentage, alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    # get the borrow fee
    borrow_fee = tx.events['BorrowFeeInROSE']['_borrowFee']
    # Get the net collateral of alice 
    net_collateral = vault_manager.getVaultColl(alice.address)
    assert net_collateral == alice_coll - borrow_fee 


def test_liquidation_normal_mode_fee(isolation, alice, bob, charlie, eren, BorrowerOps, VaultManager, StabilityPool, OSDToken, MockV3Aggregator):
    ### Description ###
    # Test to check whether equal liquidation profits are split between the OrumFeeDistribution contract and the Stability Pool
    # Get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    mock_aggregator = MockV3Aggregator[-1]
    # vault data
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei(1e18)
    alice_debt, alice_coll = Wei(2000e18), Wei('2 ether')
    bob_debt, bob_coll= Wei(1000e18), Wei('1 ether')
    charlie_debt, charlie_coll = Wei(1800e18), Wei('1 ether')
    # open 3 vaults
    borrower_ops.openVault(maxFeePercentage, alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(maxFeePercentage, bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(maxFeePercentage, charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # send some OSD to eren to deposit into the stability pool, although any vault owner like alice or bob could also deposit OSD directly
    osd_token.transfer(eren, Wei(1900e18), {"from": alice})
    # eren deposits OSD into the stability pool
    stability_pool.provideToSP(Wei(1900e18), {"from": eren})
    # push the system into recovery mode by manually haemorrhaging the ROSE/USD price
    mock_aggregator.updateAnswer(Wei(2000e8))
    # liquidate charlie
    tx = vault_manager.liquidate(charlie.address, {"from": eren})
    # get the liquidation profits distributed to the stability pool and OrumFeeDistribution
    orum_liquidation_profit = tx.events['TEST_liquidationfee']['_totalCollToSendToOrumRevenue']
    sp_liquidation_profit = tx.events['TEST_liquidationfee']['_totalCollToSendToSP']
    total_liquidation_profit = tx.events['Liquidation']['_liquidatedColl']
    assert orum_liquidation_profit == sp_liquidation_profit
    assert total_liquidation_profit == orum_liquidation_profit + sp_liquidation_profit

