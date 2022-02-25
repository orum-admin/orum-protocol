from dis import Bytecode
from brownie import accounts, Wei, chain, network
from brownie import (MockV3Aggregator, ActivePool, DefaultPool, CollSurplusPool, BorrowerOps, VaultManager,
    GasPool, HintHelpers, OSDToken, SortedVaults, StabilityPool, PriceFeed, VotedEscrow, MockV3Aggregator, CommunityIssuance, YuzuLP, YuzuPool, OrumToken, OrumFeeDistribution, LockupContractFactory)
from scripts.utils.helpful_scripts import *
from web3 import HTTPProvider, Web3

owner_rose = accounts.add('0xaa3e706e010da850bbde28699f3ed8a5b518bbaaed4b8c19fee5eb95f6fdd815')

my_address = "0xE8e4Ddc123b02Df44AD7e41225ae63e3842D40F7"
depositor_address = "0x4F81C09121F3c220A568dCb39a7F558568f3898E"
private_key = "aa3e706e010da850bbde28699f3ed8a5b518bbaaed4b8c19fee5eb95f6fdd815"
chain_id = 42261
w3 = Web3(Web3.HTTPProvider('https://testnet.emerald.oasis.dev'))

def sign_deploy(contract, *args):
    transaction = contract.constructor(*args).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": w3.eth.getTransactionCount(my_address),
    })
    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress
    
def set_addresses(contract, *args):
    transaction = contract.functions.setAddresses(*args).buildTransaction(
        {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": w3.eth.getTransactionCount(my_address),
    })
    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

def set_address(contract, *args):
    transaction = contract.functions.setAddress(*args).buildTransaction(
        {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": w3.eth.getTransactionCount(my_address),
    })
    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

def set_params(contract, *args):
    transaction = contract.functions.setParams(*args).buildTransaction(
        {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": w3.eth.getTransactionCount(my_address),
    })
    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

def deploy_oasis():
    ####### deploy all the contracts #######

    mockV3Aggregator = w3.eth.contract(abi=MockV3Aggregator.abi, bytecode=MockV3Aggregator.bytecode)
    price_aggregator_address = sign_deploy(mockV3Aggregator, int(18), int(4000e18))
    print("price_aggregator_address: ", price_aggregator_address)

    price_feed = w3.eth.contract(abi=PriceFeed.abi, bytecode=PriceFeed.bytecode) 
    price_feed_address = sign_deploy(price_feed)
    print("price_feed_address: ", price_feed_address)

    borrower_ops = w3.eth.contract(abi=BorrowerOps.abi, bytecode= BorrowerOps.bytecode)
    borrower_ops_address = sign_deploy(borrower_ops)
    print("borrower_ops_address: ", borrower_ops_address)

    vault_manager = w3.eth.contract(abi=VaultManager.abi, bytecode=VaultManager.bytecode)
    vault_manager_address = sign_deploy(vault_manager)
    print("vault_manager_address: ", vault_manager_address)

    active_pool = w3.eth.contract(abi=ActivePool.abi, bytecode=ActivePool.bytecode)
    active_pool_address = sign_deploy(active_pool)
    print("active_pool_address: ", active_pool_address)

    default_pool = w3.eth.contract(abi=DefaultPool.abi, bytecode=DefaultPool.bytecode)
    default_pool_address = sign_deploy(default_pool)
    print("default_pool_address: ", default_pool_address)

    stability_pool = w3.eth.contract(abi=StabilityPool.abi, bytecode=StabilityPool.bytecode)
    stability_pool_address = sign_deploy(stability_pool)
    print("stability_pool_address: ", stability_pool_address)

    collsurplus_pool = w3.eth.contract(abi=CollSurplusPool.abi, bytecode=CollSurplusPool.bytecode)
    collsurplus_pool_address = sign_deploy(collsurplus_pool)
    print("collsurplus_pool_address: ", collsurplus_pool_address)

    gas_pool = w3.eth.contract(abi=GasPool.abi, bytecode=GasPool.bytecode)
    gas_pool_address = sign_deploy(gas_pool)
    print("gas_pool_address: ", gas_pool_address)

    hint_helpers = w3.eth.contract(abi=HintHelpers.abi, bytecode=HintHelpers.bytecode)
    hint_helper_address = sign_deploy(hint_helpers)
    print("hint_helper_address: ", hint_helper_address)

    sorted_vaults = w3.eth.contract(abi=SortedVaults.abi, bytecode=SortedVaults.bytecode)
    sorted_vaults_address = sign_deploy(sorted_vaults)
    print("sorted_vaults_address: ", sorted_vaults_address)

    osd_token = w3.eth.contract(abi=OSDToken.abi, bytecode=OSDToken.bytecode)
    osd_token_address = sign_deploy(osd_token, vault_manager_address, stability_pool_address, borrower_ops_address)
    print("osd_token_address: ", osd_token_address)

    community_issuance = w3.eth.contract(abi=CommunityIssuance.abi, bytecode=CommunityIssuance.bytecode)
    community_issuance_address = sign_deploy(community_issuance)
    print("community_issuance_address: ", community_issuance_address)

    yuzu_lp_token = w3.eth.contract(abi=YuzuLP.abi, bytecode=YuzuLP.bytecode)
    yuzu_lp_token_address = sign_deploy(yuzu_lp_token)
    print("yuzu_lp_token_address: ", yuzu_lp_token_address)

    yuzu_lp_rewards = w3.eth.contract(abi=YuzuPool.abi, bytecode=YuzuPool.bytecode)
    yuzu_lp_rewards_address = sign_deploy(yuzu_lp_rewards)
    print("yuzu_lp_rewards_address: ", yuzu_lp_rewards_address)

    orum_token = w3.eth.contract(abi=OrumToken.abi, bytecode=OrumToken.bytecode)
    orum_token_address = sign_deploy(orum_token, community_issuance_address, yuzu_lp_rewards_address, depositor_address)
    print("orum_token_address: ", orum_token_address)

    voted_escrow = w3.eth.contract(abi=VotedEscrow.abi, bytecode=VotedEscrow.bytecode)
    voted_escrow_address = sign_deploy(voted_escrow, orum_token_address)
    print("voted_escrow_address: ", voted_escrow_address)

    orum_fee_distribution = w3.eth.contract(abi=OrumFeeDistribution.abi, bytecode=OrumFeeDistribution.bytecode)
    orum_fee_distribution_address = sign_deploy(orum_fee_distribution, voted_escrow_address)
    print("orum_fee_distribution_address: ", orum_fee_distribution_address)

    ####### Link addresses between the contracts #######
    price_feed = w3.eth.contract(address=price_feed_address, abi=PriceFeed.abi)
    set_address(price_feed, price_aggregator_address)

    borrower_ops = w3.eth.contract(address=borrower_ops_address, abi=BorrowerOps.abi)
    set_addresses(borrower_ops, vault_manager_address, active_pool_address, default_pool_address, stability_pool_address, gas_pool_address, collsurplus_pool_address, price_feed_address, sorted_vaults_address, osd_token_address, depositor_address)
    
    vault_manager = w3.eth.contract(address=vault_manager_address, abi=VaultManager.abi)
    set_addresses(vault_manager, borrower_ops_address, active_pool_address, default_pool_address, stability_pool_address, gas_pool_address, collsurplus_pool_address, price_feed_address, osd_token_address, sorted_vaults_address, depositor_address)
    
    active_pool = w3.eth.contract(address=active_pool_address, abi=ActivePool.abi)
    set_addresses(active_pool, borrower_ops_address, vault_manager_address, stability_pool_address, default_pool_address)

    default_pool = w3.eth.contract(address=default_pool_address, abi=DefaultPool.abi)
    set_addresses(default_pool, vault_manager_address, active_pool_address)

    stability_pool = w3.eth.contract(address=stability_pool_address, abi=StabilityPool.abi)
    set_addresses(stability_pool, borrower_ops_address, vault_manager_address, active_pool_address, osd_token_address, sorted_vaults_address,
                                price_feed_address, community_issuance_address)

    collsurplus_pool = w3.eth.contract(address=collsurplus_pool_address, abi=CollSurplusPool.abi)
    set_addresses(collsurplus_pool, borrower_ops_address, vault_manager_address, active_pool_address)

    sorted_vaults = w3.eth.contract(address=sorted_vaults_address, abi=SortedVaults.abi)
    set_params(sorted_vaults, int(2**256-1), vault_manager_address, borrower_ops_address)

    hint_helpers = w3.eth.contract(address=hint_helper_address, abi=HintHelpers.abi)
    set_addresses(hint_helpers, sorted_vaults_address, vault_manager_address)

    community_issuance = w3.eth.contract(address=community_issuance_address, abi=CommunityIssuance.abi)
    set_addresses(community_issuance, orum_token_address, stability_pool_address)

    yuzu_lp_rewards = w3.eth.contract(address=yuzu_lp_rewards_address, abi=YuzuPool.abi)
    set_params(yuzu_lp_rewards, orum_token_address, yuzu_lp_token_address, int(21 * 7 * 86400))

    orum_fee_distribution = w3.eth.contract(address=orum_fee_distribution_address, abi=OrumFeeDistribution.abi)
    set_addresses(orum_fee_distribution, borrower_ops_address, active_pool_address)

def deploy_eth():
    owner = accounts.add(config['wallet']['from_key'])
    depositor = '0xb9adc047b5b5155a710a0335df3AEa82CEC7EF4C'
    ####### deploy all the contracts #######
    price_aggregator_address = MockV3Aggregator.deploy(18, 4000e18, {"from": owner}, publish_source=True)
    price_feed = PriceFeed.deploy({"from": owner}, publish_source=True)  
    borrower_ops = BorrowerOps.deploy({"from":owner}, publish_source=True)
    vault_manager = VaultManager.deploy({"from": owner}, publish_source=True)
    active_pool = ActivePool.deploy({"from": owner}, publish_source=True)
    default_pool = DefaultPool.deploy({"from": owner}, publish_source=True)
    stability_pool = StabilityPool.deploy({"from": owner}, publish_source=True)
    collsurplus_pool = CollSurplusPool.deploy({"from": owner}, publish_source=True)
    gas_pool = GasPool.deploy({"from": owner}, publish_source=True)
    hint_helpers = HintHelpers.deploy({"from": owner}, publish_source=True)
    sorted_vaults = SortedVaults.deploy({"from": owner}, publish_source=True)
    osd_token = OSDToken.deploy(vault_manager.address, stability_pool.address, borrower_ops.address, {"from": owner}, publish_source=True)
    community_issuance = CommunityIssuance.deploy({"from": owner}, publish_source=True)
    yuzu_lp_token = YuzuLP.deploy({"from": owner}, publish_source=True)
    yuzu_lp_rewards = YuzuPool.deploy({"from": owner}, publish_source=True)
    lockup_contract_factory = LockupContractFactory.deploy({"from": owner}, publish_source=True)
    orum_token = OrumToken.deploy(community_issuance.address, yuzu_lp_rewards.address, depositor,  {"from": owner}, publish_source=True)
    voted_escrow = VotedEscrow.deploy(orum_token.address, {"from": owner}, publish_source=True)
    orum_revenue = OrumFeeDistribution.deploy(voted_escrow.address,{"from": owner}, publish_source=True)

    ####### Link addresses between the co

    ####### Link addresses between the contracts #######
    price_feed.setAddress(price_aggregator_address,{"from": owner})
    borrower_ops.setAddresses(vault_manager.address, active_pool.address, default_pool.address, stability_pool.address, gas_pool.address,
                              collsurplus_pool.address, price_feed.address, sorted_vaults.address, osd_token.address, depositor, {"from": owner})
    vault_manager.setAddresses(borrower_ops.address, active_pool.address, default_pool.address, stability_pool.address, gas_pool.address,
                               collsurplus_pool.address, price_feed.address, osd_token.address, sorted_vaults.address, depositor, {"from": owner})
    active_pool.setAddresses(borrower_ops.address, vault_manager.address, stability_pool.address, default_pool.address, {"from": owner})
    default_pool.setAddresses(vault_manager.address, active_pool.address, {"from": owner})
    stability_pool.setAddresses(borrower_ops.address, vault_manager.address, active_pool.address, osd_token.address, sorted_vaults.address,
                                price_feed.address, community_issuance.address, {"from": owner})
    collsurplus_pool.setAddresses(borrower_ops.address, vault_manager.address, active_pool.address,{"from": owner})
    sorted_vaults.setParams(Wei(100e18), vault_manager.address, borrower_ops.address, {"from": owner})
    hint_helpers.setAddresses(sorted_vaults.address, vault_manager.address, {"from": owner})
    community_issuance.setAddresses(orum_token.address, stability_pool.address, {"from": owner})
    yuzu_lp_rewards.setParams(orum_token.address, yuzu_lp_token.address, 21 * 7 * 86400, {"from": owner})
    lockup_contract_factory.setOrumTokenAddress(orum_token.address, {"from": owner})
    orum_revenue.setAddresses(borrower_ops.address, active_pool.address, {"from": owner})


def main():
    deploy_oasis()
    # deploy_eth()