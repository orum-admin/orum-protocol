from brownie import MockV3Aggregator, accounts, config, Wei
import requests
from decimal import Decimal

from scripts.utils.helpful_scripts import get_accounts

# get the MockV3Aggregator contract instance deployed on the mainnet (or rinkeby)
mock_aggregator = MockV3Aggregator.at('0x3205F3D888502b9b897dB120c72531399c82a325')
account = get_accounts()

def update_oracle():
    # get the ROSE/USD price feed from binance 
    res = requests.get('https://api1.binance.com/api/v3/ticker/price?symbol=ROSEUSDT').json()
    if res['symbol'] == 'ROSEUSDT':
        price = int(Decimal(res['price']) * 10**18)
    mock_aggregator.updateAnswer(Wei(price), {'from': account})



def get_account():
    # Get the price feed updator wallet account
    return accounts.load(config['wallet']['from_key'])

def main():
    update_oracle()