from brownie import Wei, exceptions, reverts
import pytest


def test_open_vault(alice, isolation, BorrowerOps, OSDToken, OrumFeeDistribution, VaultManager):
    # parameters
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei('1 ether')
    debt= Wei(500e18)
    coll = Wei(1e18)

    tx = BorrowerOps[-1].openVault(maxFeePercentage, debt, address_hint, address_hint, {"from": alice, "value": coll})
    rose_fee_1 = tx.events['BorrowFeeInROSE']['_borrowFee']
    check_true = rose_fee_1 == OrumFeeDistribution[-1].balance()
    # check if osd is allocated correctly
    check_true = check_true and (OSDToken[-1].balanceOf(alice.address) == debt)
    # check the net debt
    check_true = check_true and VaultManager[-1].getVaultDebt(alice.address) == (debt + VaultManager[-1].OSD_GAS_COMPENSATION())

    assert check_true == True

def test_open_vault_critical(alice, bob, charlie, katy, isolation, BorrowerOps, Treasury, MockV3Aggregator, OUSDToken, VaultManager):
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
    with reverts():
        borrower_ops.openVault(Wei(1e18), Wei(1500e18), address_hint, address_hint, {"from": katy, "value": Wei(1e18)})


def test_open_withdraw_repay_vault(alice, bob, isolation, OrumFeeDistribution, BorrowerOps, OSDToken, history):
    # parameters
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei('1 ether')
    debt_1= Wei(500e18)
    debt_2 = Wei(500e18)
    coll = Wei(1e18)

    BorrowerOps[-1].openVault(maxFeePercentage, debt_1, address_hint, address_hint, {"from": alice, "value": coll})
    rose_fee = history[-1].events['BorrowFeeInROSE']['_borrowFee']
    BorrowerOps[-1].openVault(maxFeePercentage, debt_1, address_hint, address_hint, {"from": bob, "value": coll})
    BorrowerOps[-1].withdrawOSD(maxFeePercentage, debt_2, address_hint, address_hint, {"from": alice})
    rose_fee += history[-1].events['BorrowFeeInROSE']['_borrowFee']
    BorrowerOps[-1].closeVault({"from": alice})
    coll_retrieved = history[-1].events['RoseSent']['_amount']
    # Collateral deposited is decreased by the rose fees charged
    check_true = coll_retrieved + rose_fee == coll
    # debt fully repayed
    check_true = check_true and OSDToken[-1].balanceOf(alice.address) == Wei(0)
    assert check_true == True


def test_open_withdraw_repay_vault(alice, bob, isolation, BorrowerOps, Treasury, OUSDToken, history):
    # parameters
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei('1 ether')
    debt_1= Wei(500e18)
    debt_2 = Wei(500e18)
    coll = Wei(1e18)
    BorrowerOps[-1].openVault(maxFeePercentage, debt_1, address_hint, address_hint, {"from": alice, "value": coll})
    rose_fee = history[-1].events['TEST_BorrowFeeSentToTreasury']['_borrowFee']
    BorrowerOps[-1].openVault(maxFeePercentage, debt_1, address_hint, address_hint, {"from": bob, "value": coll})
    BorrowerOps[-1].withdrawOUSD(maxFeePercentage, debt_2, address_hint, address_hint, {"from": alice})
    rose_fee += history[-1].events['TEST_BorrowFeeSentToTreasury']['_borrowFee']
    BorrowerOps[-1].closeVault({"from": alice})
    coll_retrieved = history[-1].events['RoseSent']['_amount']
    # Collateral deposited is decreased by the rose fees charged
    check_true = coll_retrieved + rose_fee == coll
    # debt fully repayed
    check_true = check_true and OUSDToken[-1].balanceOf(alice.address) == Wei(0)
    assert check_true == True

def test_condition_ICR_less_than_MCR(alice, isolation, BorrowerOps, history):             
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei('1 ether')
    debt = Wei(500000e18)
    coll = Wei(1e18)

    with pytest.raises(exceptions.VirtualMachineError):                         # But we are expecting this error, so we are reaising expection on this error
        BorrowerOps[-1].openVault(maxFeePercentage, debt, address_hint, address_hint, {"from": alice, "value": coll})

def test_adds_correct_coll(alice, isolation, OSDToken, BorrowerOps, history): #           # addColl(), active Trove: adds the correct collateral amount to the Trove
    address_hint = '0x'+'0'*40
    maxFeePercentage = Wei('1 ether')
    debt_1= Wei(500e18)
    coll = Wei(1e18)
    borrower_ops = BorrowerOps[-1]
    tx = borrower_ops.openVault(maxFeePercentage, debt_1, address_hint, address_hint, {"from": alice, "value": coll})
    assert debt_1 == OSDToken[-1].balanceOf(alice.address)