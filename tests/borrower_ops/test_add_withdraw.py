from brownie import Wei, reverts

def test_open_withdraw_debt_normal_mode(alice, isolation, BorrowerOps, OrumFeeDistribution, history):
    # parameters
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei('1 ether')
    debt_1= Wei(500e18)
    debt_2 = Wei(500e18)
    coll = Wei(1e18)
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    orum_revenue = OrumFeeDistribution[-1]

    ## Open a vault
    tx = borrower_ops.openVault(maxFeePercentage, debt_1, address_hint, address_hint, {"from": alice, "value": coll})
    rose_fee_orum_revenue = tx.events['BorrowFeeInROSE']['_borrowFee']

    # withdraw additional debt from the vault
    tx = borrower_ops.withdrawOSD(maxFeePercentage, debt_2, address_hint, address_hint, {"from": alice})
    rose_fee_orum_revenue += tx.events['BorrowFeeInROSE']['_borrowFee']

    orum_revenue_balance = orum_revenue.balance()
    # check if orum revenue is getting the right amount
    check_true = rose_fee_orum_revenue == orum_revenue_balance

    assert check_true == True

def test_open_withdraw_debt_critical_mode(alice, bob, charlie, isolation, BorrowerOps, MockV3Aggregator):
    # data parameters
    address_hint = '0x'+'0'*40
    # get the lastest deployed contracts
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    # Open 3 vaults in normal mode
    borrower_ops.openVault(Wei(1e18), Wei(1500e18), address_hint, address_hint, {"from": alice, "value":Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), Wei(900e18), address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), Wei(1500e18), address_hint, address_hint, {"from": charlie, "value": Wei(1e18)})

    # Manually decrease the price of ROSE to push the system into critical mode
    mock_aggregator.updateAnswer(200000000000, {"from": bob})
    # Withdraw osd in critical mode should cause to revert 
    with reverts():
        borrower_ops.withdrawOSD(Wei(1e18), Wei(500e18), address_hint, address_hint, {"from":alice})
    
def test_open_withdraw_coll_normal_mode(alice, bob, isolation, BorrowerOps, VaultManager):
    # data parameters
    address_hint = '0x'+'0'*40
    alice_coll = Wei('1 ether')
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    vault_manager = VaultManager[-1]
    # Open 2 vaults
    tx = borrower_ops.openVault(Wei(1e18), Wei(500e18), address_hint, address_hint, {"from": alice, "value": alice_coll})
    rose_fee = tx.events['BorrowFeeInROSE']['_borrowFee']
    borrower_ops.openVault(Wei(1e18), Wei(700e18), address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    # withdraw alice's collateral
    withdraw_amount = Wei(1e17)
    borrower_ops.withdrawColl(withdraw_amount, address_hint, address_hint, {"from": alice})
    # Alice's initial deposited coll should equate the sum of amount withdraw, borrow fee, vault collateral balance
    assert alice_coll == (withdraw_amount + rose_fee + vault_manager.getVaultColl(alice.address))

def test_open_withdraw_coll_critical_mode(alice, bob, charlie, isolation, BorrowerOps, MockV3Aggregator):
    # data parameter
    address_hint = '0x'+'0'*40
    alice_coll = Wei(1e18)
    # get the latest deployed contracts
    borrower_ops = BorrowerOps[-1]
    mock_aggregator = MockV3Aggregator[-1]
    # Open 3 vaults
    borrower_ops.openVault(Wei(1e18), Wei(1500e18), address_hint, address_hint, {"from": alice, "value":Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), Wei(900e18), address_hint, address_hint, {"from": bob, "value": Wei(1e18)})
    borrower_ops.openVault(Wei(1e18), Wei(1500e18), address_hint, address_hint, {"from": charlie, "value": Wei(1e18)})
    # Manually decrease the price of ROSE to push the system into critical mode
    mock_aggregator.updateAnswer(200000000000, {"from": bob})
    # withdraw alice's collateral
    withdraw_amount = Wei(1e17)
    # withdrawing collateral in critical mode should cause to revert
    with reverts():
        borrower_ops.withdrawColl(withdraw_amount, address_hint, address_hint)


    

    



