from brownie import Wei, chain

def test_liquidate_single_vault_ICR_less_than_100(isolation, alice, bob, charlie, katy, lauren, owner, BorrowerOps, VaultManager, StabilityPool, MockV3Aggregator, OrumFeeDistribution, OSDToken):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt, alice_coll = Wei(2000e18), Wei(1e18)
    bob_debt, bob_coll = Wei(1900e18), Wei(1e18)
    charlie_debt, charlie_coll = Wei(2800e18), Wei(1e18) # charlie is near limit ~4000/1.35=2960
    lauren_debt, lauren_coll = Wei(1000e18), Wei(1e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # open a vault
    borrower_ops.openVault(Wei(1e18), lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # transfer some osd to katy
    osd_token.transfer(katy, Wei(250), {"from": bob})
    # provide osd to the stability pool
    stability_pool.provideToSP(Wei(250), {"from": katy})
    # push the system into critical mode by manually decreasing the price
    mock_aggregator.updateAnswer(Wei(2000e18))
    # stability pool's osd deposits before liquidation
    prev_amount = stability_pool.getTotalOSDDeposits()
    # get the the orum revenue's balance before liquidation
    init_orum_revenue_balance = orum_revenue.balance()
    # liquidate charlie's vault
    vault_manager.liquidate(charlie)
    # get the orum revenue balance after liquidation
    curr_orum_revenue_balance = orum_revenue.balance()
    # check charlie's vault's status
    assert vault_manager.Vaults(charlie)[3] == 3
    # the profit gained from liquidation must be zero in the current scenario
    assert init_orum_revenue_balance == curr_orum_revenue_balance
    # under the condition where a vault's ICR < 100%, the debt is distributed to active vaults and not offset by the stability pool
    assert stability_pool.getTotalOSDDeposits() == prev_amount


def test_liquidate_n_vaults_ICR_less_than_100(isolation, alice, bob, charlie, katy, lauren, owner, OrumFeeDistribution, BorrowerOps, VaultManager, StabilityPool, MockV3Aggregator, OSDToken):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt, alice_coll = Wei(1900e18), Wei(1e18)
    bob_debt, bob_coll = Wei(2000e18), Wei(1e18)
    charlie_debt, charlie_coll = Wei(2800e18), Wei(1e18) # charlie is near limit ~4000/1.35=2960
    lauren_debt, lauren_coll = Wei(1000e18), Wei(1e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # open a vault
    borrower_ops.openVault(Wei(1e18), lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # transfer some osd to katy
    osd_token.transfer(katy, Wei(250), {"from": bob})
    # provide osd to the stability pool
    stability_pool.provideToSP(Wei(250), {"from": katy})
    # push the system into critical mode by manually decreasing the price
    mock_aggregator.updateAnswer(Wei(2000e18))
    # stability pool's osd deposits before liquidation
    prev_amount = stability_pool.getTotalOSDDeposits()
    # orum revenue balance before liquidation
    init_orum_revenue_balance = orum_revenue.balance()
    # liquidate charlie's vault
    vault_manager.liquidateVaults(2)
    # orum revenue balance after liquidation
    curr_orum_reevnue_balance = orum_revenue.balance()
    # the orum revenue's balance should not change in the current scenario
    assert init_orum_revenue_balance == curr_orum_reevnue_balance
    # check charlie's and bob's vault's status
    assert vault_manager.Vaults(charlie)[3] == 3 and vault_manager.Vaults(bob)[3] == 3
    # under the condition where a vault's ICR < 100%, the debt is distributed to active vaults and not offset by the stability pool
    assert stability_pool.getTotalOSDDeposits() == prev_amount


def test_liquidate_single_vault_full_offset_ICR_less_than_MCR_more_than_100(isolation, owner, OrumFeeDistribution, lauren, alice, bob, charlie, katy, BorrowerOps, VaultManager, StabilityPool, MockV3Aggregator, OSDToken):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt, alice_coll = Wei(1800e18), Wei(1e18) 
    bob_debt, bob_coll = Wei(1600e18), Wei(1e18) # ICR ~ 125% at ETH/USD = 2000
    charlie_debt, charlie_coll = Wei(1600e18), Wei(1e18) # ICR ~ 125%
    lauren_debt, lauren_coll = Wei(4000e18), Wei(2e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # open a vault
    borrower_ops.openVault(Wei(1e18), lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    vault_manager.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # transfer some osd to katy
    osd_token.transfer(katy, Wei(2800e18), {"from": lauren})
    # provide osd to the stability pool
    stability_pool.provideToSP(Wei(2800e18), {"from": katy})
    # push the system into critical mode by manually decreasing the price
    mock_aggregator.updateAnswer(Wei(2000e18))
    # stability pool's osd deposits before liquidation
    prev_amount = stability_pool.getTotalOSDDeposits()
    # orum revenue's balance before liquidation
    init_orum_revenue_balance = orum_revenue.balance()
    # liquidate charlie's vault
    tx = vault_manager.liquidate(charlie)
    # orum revenue's balance after liquidation
    curr_orum_revenue_balance = orum_revenue.balance()
    # liquidation gain of stability pool and orum revenue after liquidating charlie
    sp_coll_gain, orum_revenue_coll_gain = tx.events['TEST_liquidationfee']['_totalCollToSendToSP'], tx.events['TEST_liquidationfee']['_totalCollToSendToOrumRevenue']
    total_liquidated_coll = tx.events['Liquidation']['_liquidatedColl']
    # the gain in ROSE balance of orum revenue should be equal to the profit made in the liquidation event
    assert curr_orum_revenue_balance - init_orum_revenue_balance == orum_revenue_coll_gain
    assert total_liquidated_coll == sp_coll_gain + orum_revenue_coll_gain
    # check charlie's and bob's vault's status
    assert vault_manager.Vaults(charlie)[3] == 3
    # under the condition where a vault's 100% < ICR < MCR and SP.OSD > vault debt, the debt is distributed to active vaults and not offset by the stability pool
    assert stability_pool.getTotalOSDDeposits() + charlie_debt + vault_manager.OSD_GAS_COMPENSATION() == prev_amount


def test_liquidate_n_vaults_full_offset_ICR_less_than_MCR_more_than_100(isolation, alice, bob, owner, lauren, charlie, katy, OrumFeeDistribution, BorrowerOps, VaultManager, StabilityPool, MockV3Aggregator, OSDToken):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt, alice_coll = Wei(1000e18), Wei(1e18) 
    bob_debt, bob_coll = Wei(1600e18), Wei(1e18) # ICR ~ 120%
    charlie_debt, charlie_coll = Wei(1600e18), Wei(1e18) # # ICR ~ 120%
    lauren_debt, lauren_coll = Wei(4000e18), Wei(3e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # open a vault
    borrower_ops.openVault(Wei(1e18), lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    vault_manager.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # transfer some ousd to katy
    osd_token.transfer(katy, Wei(4000e18), {"from": lauren})
    # provide ousd to the stability pool
    stability_pool.provideToSP(Wei(4000e18), {"from": katy})
    # push the system into critical mode by manually decreasing the price
    mock_aggregator.updateAnswer(Wei(2000e18))
    # stability pool's osd deposits before liquidation
    prev_amount = stability_pool.getTotalOSDDeposits()
    # orum revenue's balance before liquidation
    init_orum_revenue_balance = orum_revenue.balance()
    # liquidate charlie's vault
    tx = vault_manager.liquidateVaults(2)
    # orum revenue's balance after liquidation
    curr_orum_revenue_balance = orum_revenue.balance()
    # check charlie's and bob's vault's status
    assert vault_manager.Vaults(charlie)[3] == 3 and vault_manager.Vaults(bob)[3] == 3
    # current balance of the treasury and nebu staking 
    curr_orum_revenue_balance = orum_revenue.balance()
    # liquidation gain of stability pool and orum revenue after liquidating charlie
    sp_coll_gain, orum_revenue_coll_gain = tx.events['TEST_liquidationfee']['_totalCollToSendToSP'], tx.events['TEST_liquidationfee']['_totalCollToSendToOrumRevenue']
    total_liquidated_coll = tx.events['Liquidation']['_liquidatedColl']
    # the gain in ROSE balance of orum revenue should be equal to the profit made in the liquidation event
    assert curr_orum_revenue_balance - init_orum_revenue_balance == orum_revenue_coll_gain
    assert total_liquidated_coll == sp_coll_gain + orum_revenue_coll_gain
    # under the condition where a vault's 100% < ICR < MCR and SP.OUSD > vault debt, the debt is distributed to active vaults and not offset by the stability pool
    assert stability_pool.getTotalOSDDeposits() + charlie_debt + bob_debt + 2 * vault_manager.OSD_GAS_COMPENSATION() == prev_amount

def test_liquidate_n_vaults_partial_offset_ICR_less_than_MCR_more_than_100(isolation, owner, lauren, alice, bob, charlie, katy, BorrowerOps, VaultManager, StabilityPool, MockV3Aggregator, OSDToken, DefaultPool, OrumFeeDistribution):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt, alice_coll = Wei(1000e18), Wei(1e18)
    bob_debt, bob_coll = Wei(1600e18), Wei(1e18) # ICR ~ 120%
    charlie_debt, charlie_coll = Wei(1600e18), Wei(1e18) # ICR ~ 120%
    lauren_debt, lauren_coll = Wei(4000e18), Wei(3e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_revenue = OrumFeeDistribution[-1]
    default_pool = DefaultPool[-1]
    # open a vault
    borrower_ops.openVault(Wei(1e18), lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    vault_manager.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # transfer some ousd to katy
    osd_token.transfer(katy, Wei(3000e18), {"from": lauren})
    # treasury and nebu staking contract's ROSE balance before liquidations
    init_orum_revenue_balance = orum_revenue.balance()
    # provide ousd to the stability pool
    stability_pool.provideToSP(Wei(3000e18), {"from": katy})
    # push the system into critical mode by manually decreasing the price
    mock_aggregator.updateAnswer(Wei(2000e18))
    # stability pool's osd deposits before liquidation
    prev_amount = stability_pool.getTotalOSDDeposits()
    # initial default pool balance
    init_default_pool_balance = default_pool.getROSE()
    # liquidate charlie's vault
    tx = vault_manager.liquidateVaults(2)
    # check charlie's and bob's vault's status
    assert vault_manager.Vaults(charlie)[3] == 3 and vault_manager.Vaults(bob)[3] == 3
    # default pool balance after liquidation
    curr_default_pool_balance = default_pool.getROSE()
    # current balance of the treasury and nebu staking 
    curr_orum_revenue_balance = orum_revenue.balance()
    # get the combined ROSE fee sent to the treasury and nebu staking contracts
    # liquidation gain of stability pool and orum revenue after liquidating charlie
    sp_coll_gain, orum_revenue_coll_gain = tx.events['TEST_liquidationfee']['_totalCollToSendToSP'], tx.events['TEST_liquidationfee']['_totalCollToSendToOrumRevenue']
    total_liquidated_coll = tx.events['Liquidation']['_liquidatedColl']
    # default pool ROSE gain is equal to the amount redistributed from the liquidation event
    default_pool_coll_gain = curr_default_pool_balance - init_default_pool_balance
    # the gain in ROSE balance of orum revenue should be equal to the profit made in the liquidation event
    assert curr_orum_revenue_balance - init_orum_revenue_balance == orum_revenue_coll_gain
    assert total_liquidated_coll == sp_coll_gain + orum_revenue_coll_gain + default_pool_coll_gain
    # under the condition where a vault's 100% < ICR < MCR and SP.OUSD < vault debt, some fraction of debt is offset by the stability pool and the remaining distributed to active vaults
    assert stability_pool.getTotalOSDDeposits() == 0


def test_liquidate_n_vaults_full_offset_ICR_more_than_MCR_less_than_TCR(isolation, owner, lauren, alice, bob, charlie, katy, OrumFeeDistribution, BorrowerOps, VaultManager, StabilityPool, MockV3Aggregator, OSDToken, CollSurplusPool):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt, alice_coll = Wei(1000e18), Wei(1e18)
    bob_debt, bob_coll = Wei(1400e18), Wei(1e18) # ICR~140% and MCR is 135%
    charlie_debt, charlie_coll = Wei(1400e18), Wei(1e18) # charlie is near limit ~2000/1.40=1600
    lauren_debt, lauren_coll = Wei(4000e18), Wei(3e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_revenue = OrumFeeDistribution[-1]
    coll_surplus_pool = CollSurplusPool[-1]
    # open a vault
    borrower_ops.openVault(Wei(1e18), lauren_debt, address_hint, address_hint, {"from": lauren, "value": lauren_coll})
    # get the initial balance of the orum_revenue contract
    init_balance = orum_revenue.balance()
    # The balance should be zero because for the first 14 days revenue is sent to an EOA
    assert init_balance == 0
    # move 14 days forward into the future
    chain.mine(timedelta=14*86400)
    borrower_ops.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    vault_manager.changeTreasuryAddress(orum_revenue.address, {"from": owner})
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # transfer some ousd to katy
    osd_token.transfer(katy, Wei(3000e18), {"from": lauren})
    # treasury and nebu staking contract's ROSE balance before liquidations
    init_orum_revenue_balance = orum_revenue.balance()
    # provide ousd to the stability pool
    stability_pool.provideToSP(Wei(3000e18), {"from": katy})
    # push the system into critical mode by manually decreasing the price
    mock_aggregator.updateAnswer(Wei(2000e18))
    # initial collSurplus pool balance
    prev_coll = coll_surplus_pool.getROSE()
    # liquidate charlie's vault
    tx = vault_manager.liquidateVaults(2)
    # check charlie's and bob's vault's status
    assert vault_manager.Vaults(charlie)[3] == 3 and vault_manager.Vaults(bob)[3] == 3
    # current balance of the treasury and nebu staking 
    curr_orum_revenue_balance = orum_revenue.balance()
    # get the combined ROSE fee sent to the treasury and nebu staking contracts
    # liquidation gain of stability pool and orum revenue after liquidating charlie
    sp_coll_gain, orum_revenue_coll_gain = tx.events['TEST_liquidationfee']['_totalCollToSendToSP'], tx.events['TEST_liquidationfee']['_totalCollToSendToOrumRevenue']
    total_liquidated_coll = tx.events['Liquidation']['_liquidatedColl']
    # the gain in ROSE balance of orum revenue should be equal to the profit made in the liquidation event
    assert curr_orum_revenue_balance - init_orum_revenue_balance == orum_revenue_coll_gain
    assert total_liquidated_coll == sp_coll_gain + orum_revenue_coll_gain
    # current collSurplus pool balance
    curr_coll = coll_surplus_pool.getROSE()
    # under the condition where a vault's MCR <= ICR < TCR and SP.OSD >= vault debt, full debt is offset by the stability pool and the extra collateral is sent to the collateral surplus pools
    assert curr_coll > prev_coll
    





