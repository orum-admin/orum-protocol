import secrets
from hashlib import sha3_256
from brownie import accounts

def generate_accounts(num):
    for _ in range(num):
        key = '0x' + sha3_256(secrets.token_bytes(50)).hexdigest()
        accounts.add(key)
    print("Total accounts: ", len(accounts))
    print("Balance of account 369: ", accounts[368].balance())

def main():
    generate_accounts(num=500)
