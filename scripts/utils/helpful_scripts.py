from brownie import (
    accounts, 
    network, 
    config,
    MockV3Aggregator,
    Wei
)

LOCAL_BLOCKCHAIN_NETWORKS = ["development", "ganache-local"]
DECIMALS = 8
STARTING_PRICE = 4000e8

def get_accounts(num=1):
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        return accounts[:num]
    else:
        return accounts.add(config['wallet']['from_key'])

def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    # if len(MockV3Aggregator) <= 0:
    mock_aggregator = MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": get_accounts()})
    print("Mocks deployed!")
    return mock_aggregator.address

    

