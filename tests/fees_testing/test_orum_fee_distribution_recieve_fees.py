from datetime import timedelta
from pyparsing import CharsNotIn
from brownie import Wei, chain

def test_orum_fee_distribution_recieve_fees_from_borrower_ops(isolation, BorrowerOps, OrumFeeDistribution, alice, eren, bob, owner):
    ### Description ###
    # Test to check whether OrumFeeDistribution contract is recieving borrow fees from the BorrowerOps contract
    # vault data
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei(1e18)
    alice_debt, alice_coll = Wei(1000e18), Wei('1 ether')
    eren_debt, eren_coll = Wei(1000e18), Wei('1 ether')
    bob_debt, bob_coll = Wei(1000e18), Wei('1 ether')
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # open a vault
    borrower_ops.openVault(maxFeePercentage, bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open vaults
    borrower_ops.openVault(maxFeePercentage, alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(maxFeePercentage, eren_debt, address_hint, address_hint, {"from": eren, "value": eren_coll})
    # check if the balance of the orum_revenue contract has been updated
    curr_balance = orum_revenue.balance()
    assert curr_balance > init_balance

def test_orum_fee_distribution_is_recieving_fees_from_liquidation(isolation, BorrowerOps, MockV3Aggregator, OSDToken, StabilityPool, OrumFeeDistribution, VaultManager, alice, eren, bob, charlie, owner, lauren):
    ### Description ###
    # Tests if the OrumFeeDistribution contract is recieving its share of the liquidation fee 
    # Get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    mock_aggregator = MockV3Aggregator[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # vault data
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei(1e18)
    alice_debt, alice_coll = Wei(2000e18), Wei('2 ether')
    bob_debt, bob_coll= Wei(1000e18), Wei('1 ether')
    charlie_debt, charlie_coll = Wei(1800e18), Wei('1 ether')
    lauren_debt, lauren_coll = Wei(1000e18), Wei('1 ether')
    # open a vault
    borrower_ops.openVault(maxFeePercentage, lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    vault_manager.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open 3 vaults
    borrower_ops.openVault(maxFeePercentage, alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(maxFeePercentage, bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(maxFeePercentage, charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # get the orum_revenue contract's balance after opening vaults
    orum_balance_init = orum_revenue.balance()
    # send some OSD to eren to deposit into the stability pool, although any vault owner like alice or bob could also deposit OSD directly
    osd_token.transfer(eren, Wei(1900e18), {"from": alice})
    # eren deposits OSD into the stability pool
    stability_pool.provideToSP(Wei(1900e18), {"from": eren})
    # push the system into recovery mode by manually haemorrhaging the ROSE/USD price
    mock_aggregator.updateAnswer(Wei(2000e8))
    # liquidate charlie
    tx = vault_manager.liquidate(charlie.address, {"from": eren})
    # get the liquidation profit distributed to the OrumFeeDistribution
    orum_liquidation_profit = tx.events['TEST_liquidationfee']['_totalCollToSendToOrumRevenue']
    # get the balance of the orum_revenue contract after liquidation
    orum_balance_curr = orum_revenue.balance()
    # check if the correct amount of revenue is sent to the orum_revenue contract
    assert orum_liquidation_profit == orum_balance_curr - orum_balance_init

def test_orum_fee_distribution_is_receiving_fees_from_liquidation_partial(isolation, BorrowerOps, MockV3Aggregator, OSDToken, StabilityPool, OrumFeeDistribution, VaultManager, alice, eren, bob, charlie, lauren, owner):
    ### Description ###
    # Tests to check whether the OrumFeeDistribution contract is receiving liquidation profits correctly
    # get the latest deployed contracts 
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    mock_aggregator = MockV3Aggregator[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # vault data
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei(1e18)
    alice_debt, alice_coll = Wei(2000e18), Wei('2 ether')
    bob_debt, bob_coll= Wei(1000e18), Wei('1 ether')
    charlie_debt, charlie_coll = Wei(1800e18), Wei('1 ether')
    lauren_debt, lauren_coll = Wei(1000e18), Wei('1 ether')
    # open a vault
    borrower_ops.openVault(maxFeePercentage, lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    vault_manager.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open vaults
    borrower_ops.openVault(maxFeePercentage, alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(maxFeePercentage, bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(maxFeePercentage, charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # initial orum revenue
    orum_balance_init = orum_revenue.balance()
    # send some OSD to eren to deposit into the stability pool, although any vault owner like alice or bob could also deposit OSD directly
    osd_token.transfer(eren, Wei(1000e18), {"from": alice})
    # eren deposits OSD into the stability pool
    stability_pool.provideToSP(Wei(1000e18), {"from": eren})
    # push the system into recovery mode by manually haemorrhaging the ROSE/USD price
    mock_aggregator.updateAnswer(Wei(2000e8))
    # liquidate charlie
    tx = vault_manager.liquidate(charlie.address, {"from": eren})
    # get the liquidation profit distributed to the OrumFeeDistribution
    orum_liquidation_profit = tx.events['TEST_liquidationfee']['_totalCollToSendToOrumRevenue']
    # get the balance of the orum_revenue contract after liquidation
    orum_balance_curr = orum_revenue.balance()
    # check if the correct amount of revenue is sent to the orum_revenue contract
    assert orum_liquidation_profit == orum_balance_curr - orum_balance_init

def test_orum_fee_distribution_is_receiving_fees_from_liquidation_redistribution(isolation, BorrowerOps, MockV3Aggregator, OSDToken, StabilityPool, OrumFeeDistribution, VaultManager, alice, bob, charlie, eren, owner, lauren):
    ### Description ###
    # Test to check whether the OrumFeeDistribution contract is receiving any profit from liquidation. In the case when the stability pool is depleted
    # all the debt is redistributed among the active vaults and no "profit" is shared with the OrumFeeDistribution contract
    # get the latest deployed contracts 
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    mock_aggregator = MockV3Aggregator[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # vault data
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei(1e18)
    alice_debt, alice_coll = Wei(2000e18), Wei('2 ether')
    bob_debt, bob_coll= Wei(1000e18), Wei('1 ether')
    charlie_debt, charlie_coll = Wei(1800e18), Wei('1 ether')
    lauren_debt, lauren_coll = Wei(1000e18), Wei('1 ether')
    # open a vault
    borrower_ops.openVault(maxFeePercentage, lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    vault_manager.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open vaults
    borrower_ops.openVault(maxFeePercentage, alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(maxFeePercentage, bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(maxFeePercentage, charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # initial orum revenue
    orum_balance_init = orum_revenue.balance()
    # push the system into recovery mode by manually haemorrhaging the ROSE/USD price
    mock_aggregator.updateAnswer(Wei(2000e8))
    # liquidate charlie
    tx = vault_manager.liquidate(charlie.address, {"from": eren})
    # get the liquidation profit distributed to the OrumFeeDistribution
    orum_liquidation_profit = tx.events['TEST_liquidationfee']['_totalCollToSendToOrumRevenue']
    # get the balance of the orum_revenue contract after liquidation
    orum_balance_curr = orum_revenue.balance()
    # check if the correct amount of revenue is sent to the orum_revenue contract
    assert orum_liquidation_profit == 0
    assert orum_balance_curr == orum_balance_init

