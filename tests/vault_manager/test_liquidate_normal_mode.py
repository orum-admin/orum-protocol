from brownie import Wei, reverts

def test_liquidate_full_offset_1_vault(isolation, alice, bob, charlie, katy, owner, lauren, VaultManager, OrumFeeDistribution, MockV3Aggregator, StabilityPool, BorrowerOps, OSDToken):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt = Wei(500e18)
    bob_debt = Wei(900e18)
    charlie_debt = Wei(200e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    orum_revenue = OrumFeeDistribution[-1]
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e17)})
    # transfer some osd to the stability pool depositors
    osd_token.transfer(katy, Wei(100e18), {"from": alice})
    osd_token.transfer(lauren, Wei(300e18), {"from": bob})
    # deposit osd into the stability pool
    stability_pool.provideToSP(Wei(100e18), {"from": katy})
    stability_pool.provideToSP(Wei(300e18), {"from": lauren})
    # push the system into critical mode by manually decreasing the exchange price drastically
    mock_aggregator.updateAnswer(Wei(2000e8))
    # liquidate the vault with the lowest ICR; in this case, charlie's vault
    vault_manager.liquidate(charlie.address, {"from": lauren})
    # check whether charlie's vault got liquidated or not
    assert vault_manager.Vaults(charlie.address)[3] == 3

def test_liquidate_full_offset_n_vaults(isolation, alice, bob, charlie, katy, lauren, VaultManager, MockV3Aggregator, StabilityPool, BorrowerOps, OSDToken):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt = Wei(500e18)
    bob_debt = Wei(900e18)
    charlie_debt = Wei(200e18)
    katy_debt = Wei(150e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    # open 4 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e17)})
    borrower_ops.openVault(Wei(1e18), katy_debt, address_hint, address_hint, {"from": katy, "value": Wei(1e17)})
    # transfer some osd to lauren
    osd_token.transfer(lauren, Wei(300e18), {"from": bob})
    osd_token.transfer(lauren, Wei(150e18), {"from": alice})
    # deposit osd into stability pool
    stability_pool.provideToSP(Wei(450e18), {"from": lauren})
    # push the system into critical mode by manually decreasing the exchange price drastically
    mock_aggregator.updateAnswer(Wei(2000e8))
    # liquidate 2 vaults with the lowest ICR; in this case, charlie's and katy's vault
    vault_manager.liquidateVaults(2, {"from": bob})
    # check whether charlie's and katy's vault got liquidated or not
    assert (vault_manager.Vaults(charlie.address)[3] == 3 and vault_manager.Vaults(katy.address)[3] == 3)

def test_liquidate_partial_offset(isolation, alice, bob, charlie, katy, lauren, VaultManager, MockV3Aggregator, StabilityPool, BorrowerOps, OSDToken, DefaultPool):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt = Wei(500e18)
    bob_debt = Wei(900e18)
    charlie_debt = Wei(200e18)
    katy_debt = Wei(150e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    default_pool = DefaultPool[-1]
    # open 4 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e17)})
    borrower_ops.openVault(Wei(1e18), katy_debt, address_hint, address_hint, {"from": katy, "value": Wei(1e17)})
    # transfer some osd to lauren
    osd_token.transfer(lauren, Wei(300e18), {"from": bob})
    # deposit osd into stability pool
    stability_pool.provideToSP(Wei(300e18), {"from": lauren})
    # push the system into critical mode by manually decreasing the exchange price drastically
    mock_aggregator.updateAnswer(Wei(2000e8))
    # Initial default pool debt and collateral
    prev_debt, prev_coll = default_pool.getOSDDebt(), default_pool.getROSE()
    # liquidate 2 vaults with the lowest ICR; in this case, charlie's and katy's vault
    vault_manager.liquidateVaults(2, {"from": bob})
    # check whether charlie's and katy's vaults have been liquidated
    assert vault_manager.Vaults(charlie.address)[3] == 3 and vault_manager.Vaults(katy.address)[3] == 3
    # check whether stability pool has 0 balance
    assert stability_pool.getTotalOSDDeposits() == 0
    # check whether debt and collateral has been redistributed between active vault owners
    curr_debt, curr_coll = default_pool.getOSDDebt(), default_pool.getROSE()
    assert prev_debt != curr_debt and prev_coll != curr_coll

    
def test_liquidate_sp_depleted(isolation, alice, bob, charlie, katy, lauren, VaultManager, MockV3Aggregator, StabilityPool, BorrowerOps, OSDToken, DefaultPool):
    # vault parameters
    address_hint = '0x'+ '0'*40
    alice_debt = Wei(500e18)
    bob_debt = Wei(900e18)
    charlie_debt = Wei(200e18)
    katy_debt = Wei(150e18)
    # get the latest deployed contracts
    vault_manager = VaultManager[-1]
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    stability_pool = StabilityPool[-1]
    osd_token = OSDToken[-1]
    default_pool = DefaultPool[-1]
    prev_amount = default_pool.getOSDDebt()
    # open 4 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e17)})
    borrower_ops.openVault(Wei(1e18), katy_debt, address_hint, address_hint, {"from": katy, "value": Wei(1e17)})
    # push the system into critical mode by manually decreasing the exchange price drastically
    mock_aggregator.updateAnswer(Wei(2000e8))
    # liquidate 2 vaults with the lowest ICR; in this case, charlie's and katy's vault
    vault_manager.liquidateVaults(2, {"from": bob})
    # check whether charlie's and katy's vaults have been liquidated
    assert vault_manager.Vaults(charlie.address)[3] == 3 and vault_manager.Vaults(katy.address)[3] == 3
    # check whether stability pool has 0 balance
    assert stability_pool.getTotalOSDDeposits() == 0
    # check whether debt redistributed is equal to the sum of the debts of liquidated vaults
    curr_debt = default_pool.getOSDDebt()
    assert curr_debt == charlie_debt + katy_debt + 2*vault_manager.OSD_GAS_COMPENSATION()


    