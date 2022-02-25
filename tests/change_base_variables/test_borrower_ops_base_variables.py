from brownie import Wei, reverts


def test_min_debt_change(isolation, BorrowerOps, alice, bob, owner):
    ### Description ###
    # Tests if the Min Debt change has taken effect
    # Vault data
    address_hint = '0x'+'0'*40
    alice_debt, alice_coll = Wei(100e18), Wei('1 ether')
    bob_debt, bob_coll  = Wei(100e18), Wei('1 ether')
    # get the latest deployed contract
    borrower_ops = BorrowerOps[-1]
    # alice should be able to open a vault with 100 OSD debt
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    # set the min debt of the protocol to be 150 OSD
    borrower_ops.changeMinNetDebt(Wei(150e18), {"from": owner})
    # it should throw an error if bob tries to open a vault with 100 OSD debt
    with reverts():
        borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})

def test_MCR_change(isolation, BorrowerOps, alice, bob, charlie, owner):
    ### Description ###
    # Increase the MCR from 150% to 200% and check if the protocol allows opening a vault 
    # with an ICR < 200%
    # vault data
    address_hint = '0x'+'0'*40
    charlie_debt, charlie_coll = Wei(100e18), Wei('3 ether')
    alice_debt, alice_coll = Wei(2600e18), Wei('1 ether') # 2600 ~= 1 * 4000 / (1.5)
    bob_debt, bob_coll  = Wei(2600e18), Wei('1 ether') 
    # opening it just to keep the TCR below CCR
    # get the latest deployed contract
    borrower_ops = BorrowerOps[-1]
    # charlie opens a vault with low debt in order to increase the TCR, otherwise the protocol would not let bob withdraw debt
    # even within his limits
    borrower_ops.openVault(Wei(1e18), charlie_debt, address_hint, address_hint, {"from": charlie, "value": charlie_coll})
    # alice should be able to open a vault with 2600 OSD debt
    borrower_ops.openVault(Wei(1e18), alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    # change the MCR of the protocol to be 200%
    borrower_ops.changeMCR(Wei(200e16), {"from": owner})
    # it should throw an error if bob is trying to withdraw 2600 OSD by depositing 1 ethereum worth (for testing purposes, we have considered 1 ETH = 4000 USD) of collateral 
    # the new borrow limit for 1 ETH is ~ (1 * 4000) / 2 = 2000 OSD
    with reverts():
        borrower_ops.openVault(Wei(1e18), bob_debt, address_hint, address_hint, {"from": bob, "value": bob_coll})

