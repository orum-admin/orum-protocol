from brownie import Wei, reverts

def test_open_normal_mode(alice, bob, charlie, isolation, BorrowerOps, OSDToken):
    # data parameters
    address_hint = '0x'+'0'*40
    alice_debt = Wei(500e18)
    bob_debt = Wei(700e18)
    charlie_debt = Wei(1500e18)
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    osd_token = OSDToken[-1]
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e18)})
    # check if each of them have been correctly allocated the debt
    check_true = alice_debt == osd_token.balanceOf(alice.address)
    check_true |= bob_debt == osd_token.balanceOf(bob.address)
    check_true |= charlie_debt == osd_token.balanceOf(charlie.address)

    assert check_true == True

def test_open_critical_mode(alice, bob, charlie, isolation, BorrowerOps, MockV3Aggregator):
    # data parameters
    address_hint = '0x'+'0'*40
    alice_debt = Wei(500e18)
    bob_debt = Wei(700e18)
    charlie_debt = Wei(1500e18)
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    # open 2 vaults in normal mode
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    # manually push the system into critical mode by drastically decreasing the exchange price
    mock_aggregator.updateAnswer(Wei(2000e8))
    with reverts():
        borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e18)})

def test_repay(alice, bob, charlie, isolation, BorrowerOps, OSDToken):
    # data parameters
    address_hint = '0x'+'0'*40
    alice_debt, alice_debt_repay = Wei(500e18), Wei(100e18)
    bob_debt, bob_debt_repay = Wei(900e18), Wei(500e18)
    charlie_debt, charlie_debt_repay = Wei(1800e18), Wei(900e18)
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    osd_token = OSDToken[-1]
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e18)})
    # repay each of the borrower's debts
    borrower_ops.repayOSD(alice_debt_repay, address_hint, address_hint, {"from": alice})
    borrower_ops.repayOSD(bob_debt_repay, address_hint, address_hint, {"from": bob})
    borrower_ops.repayOSD(charlie_debt_repay, address_hint, address_hint, {"from": charlie})
    # check if each of them has repayed correctly
    check_true = (alice_debt - alice_debt_repay) == osd_token.balanceOf(alice.address)
    check_true |= (bob_debt - bob_debt_repay) == osd_token.balanceOf(bob.address)
    check_true |= (charlie_debt - charlie_debt_repay) == osd_token.balanceOf(charlie.address)

    assert check_true == True

def test_close(alice, bob, charlie, isolation, BorrowerOps, VaultManager, OSDToken):
    # data parameters
    address_hint = '0x'+'0'*40
    alice_debt = Wei(500e18)
    bob_debt = Wei(700e18)
    charlie_debt = Wei(1500e18)
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    osd_token = OSDToken[-1]
    vault_manager = VaultManager[-1]
    # open 3 vaults
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": Wei(1e18)})
    # close vaults of each of the borrowers
    borrower_ops.closeVault({"from": alice})
    borrower_ops.closeVault({"from": bob})
    # check the osd balances of the users
    check_true_osd = osd_token.balanceOf(alice.address) == Wei(0)
    check_true_osd = check_true_osd and osd_token.balanceOf(bob.address) == Wei(0)
    # check the vault statuses of the users
    # Vault closedByOwner status value: 2
    check_true_vault = vault_manager.getVaultStatus(alice.address) == 2
    check_true_vault = check_true_vault and vault_manager.getVaultStatus(bob.address) == 2

    assert (check_true_osd == True and check_true_vault == True)
