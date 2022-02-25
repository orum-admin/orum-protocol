import pytest
from brownie import accounts, Wei, chain
from brownie import (MockV3Aggregator, ActivePool, DefaultPool, CollSurplusPool, BorrowerOps, VaultManager,
    GasPool, HintHelpers, OSDToken, SortedVaults, StabilityPool, PriceFeed, VotedEscrow, MockV3Aggregator, CommunityIssuance, YuzuLP, YuzuPool, OrumToken, OrumFeeDistribution, LockupContractFactory)
from scripts.utils.helpful_scripts import *

@pytest.fixture(scope="module", autouse="True")
def shared_setup(module_isolation):
    pass

@pytest.fixture(scope="module")
def owner():
    return accounts[0]

@pytest.fixture(scope="module")
def alice():
    return accounts[1]

@pytest.fixture(scope="module")
def bob():
    return accounts[2]

@pytest.fixture(scope="module")
def charlie():
    return accounts[3]

@pytest.fixture(scope="module")
def katy():
    return accounts[4]

@pytest.fixture(scope="module")
def lauren():
    return accounts[5]
@pytest.fixture(scope="module")
def eren():
    return accounts[6]

@pytest.fixture(scope="module")
def ash():
    return accounts[7]

@pytest.fixture(scope="module")
def users():
    return accounts[8:]

@pytest.fixture(scope="module", autouse=True)
def deploy(owner, alice, bob, katy, eren, charlie):
    ####### deploy all the contracts #######
    price_aggregator_address = MockV3Aggregator.deploy(18, 4000e18, {"from": owner})
    price_feed = PriceFeed.deploy({"from": owner})  
    borrower_ops = BorrowerOps.deploy({"from":owner})
    vault_manager = VaultManager.deploy({"from": owner})
    active_pool = ActivePool.deploy({"from": owner})
    default_pool = DefaultPool.deploy({"from": owner})
    stability_pool = StabilityPool.deploy({"from": owner})
    collsurplus_pool = CollSurplusPool.deploy({"from": owner})
    gas_pool = GasPool.deploy({"from": owner})
    hint_helpers = HintHelpers.deploy({"from": owner})
    sorted_vaults = SortedVaults.deploy({"from": owner})
    osd_token = OSDToken.deploy(vault_manager.address, stability_pool.address, borrower_ops.address, {"from": owner})
    community_issuance = CommunityIssuance.deploy({"from": owner})
    yuzu_lp_token = YuzuLP.deploy({"from": owner})
    yuzu_lp_rewards = YuzuPool.deploy({"from": owner})
    lockup_contract_factory = LockupContractFactory.deploy({"from": owner})
    orum_token = OrumToken.deploy(community_issuance.address, yuzu_lp_rewards.address, eren.address,  {"from": owner})
    voted_escrow = VotedEscrow.deploy(orum_token.address, {"from": owner})
    orum_revenue = OrumFeeDistribution.deploy(voted_escrow.address,{"from": owner})

    ####### Link addresses between the contracts #######
    price_feed.setAddress(price_aggregator_address,{"from": owner})
    borrower_ops.setAddresses(vault_manager.address, active_pool.address, default_pool.address, stability_pool.address, gas_pool.address,
                              collsurplus_pool.address, price_feed.address, sorted_vaults.address, osd_token.address, eren.address, {"from": owner})
    vault_manager.setAddresses(borrower_ops.address, active_pool.address, default_pool.address, stability_pool.address, gas_pool.address,
                               collsurplus_pool.address, price_feed.address, osd_token.address, sorted_vaults.address, eren.address, {"from": owner})
    active_pool.setAddresses(borrower_ops.address, vault_manager.address, stability_pool.address, default_pool.address, {"from": owner})
    default_pool.setAddresses(vault_manager.address, active_pool.address, {"from": owner})
    stability_pool.setAddresses(borrower_ops.address, vault_manager.address, active_pool.address, osd_token.address, sorted_vaults.address,
                                price_feed.address, community_issuance.address, {"from": owner})
    collsurplus_pool.setAddresses(borrower_ops.address, vault_manager.address, active_pool.address,{"from": owner})
    sorted_vaults.setParams(Wei(100e18), vault_manager.address, borrower_ops.address, {"from": owner})
    hint_helpers.setAddresses(sorted_vaults.address, vault_manager.address, {"from": owner})
    # orum_staking.setAddresses(orum_token.address, osd_token.address, vault_manager.address, borrower_ops.address, active_pool.address, {"from": owner})
    community_issuance.setAddresses(orum_token.address, stability_pool.address, {"from": owner})
    yuzu_lp_rewards.setParams(orum_token.address, yuzu_lp_token.address, 5 * 30 * 86400, {"from": owner})
    lockup_contract_factory.setOrumTokenAddress(orum_token.address, {"from": owner})
    orum_revenue.setAddresses(borrower_ops.address, active_pool.address, {"from": owner})
    # katy can claim orum tokens after a lockup period of one year.
    # lockup_contract_factory.deployLockupContract(katy.address, chain.time() + int(7 * 86400), {"from": owner})



    # orum_revenue.setAddresses(borrower_ops.address, vault_manager.address)