from brownie import Wei, chain
from math import ceil

def test_orum_emissions_to_stability_pool(isolation, BorrowerOps, StabilityPool, CommunityIssuance, OrumToken, alice):
    # Get the latest depoloyments of the contracts
    borrower_ops = BorrowerOps[-1]
    stability_pool = StabilityPool[-1]
    community_issuance = CommunityIssuance[-1]
    orum_token = OrumToken[-1]
    # vault data
    address_hint = '0x' + '0'*40
    maxFeePercentage = Wei(1e18)
    alice_debt = Wei(1000e18)
    alice_coll = Wei("1 ether")
    # alice opens a vault
    borrower_ops.openVault(maxFeePercentage, alice_debt, address_hint, address_hint, {"from": alice, "value": alice_coll})
    # alice deposits OSD into the stability pool and farms Orum tokens
    stability_pool.provideToSP(alice_debt, {"from": alice})
    # go 1 year into the future and check whether the Orum she has recieved is equal to the total issuance for that year
    # to trigger Orum emission, alice has to interact with the stability pool, i.e, withdrawing some OSD deposited in this case
    chain.mine(timedelta=365*86400)
    stability_pool.withdrawFromSP(Wei(10e18), {"from": alice})
    assert ceil(community_issuance.totalOrumIssued() / (10 ** 24)) == int(40 * 0.5)
    # go one more year and trigger Orum issuance
    chain.mine(timedelta=365*86400)
    stability_pool.withdrawFromSP(Wei(10e18), {"from": alice})
    assert ceil(community_issuance.totalOrumIssued() / (10 ** 24)) == ceil(40 * (0.50 + (1 - 0.5)/2)) # 0.75
    # go one more year and trigger Orum issuance
    chain.mine(timedelta=365*86400)
    stability_pool.withdrawFromSP(Wei(10e18), {"from": alice})
    assert ceil(community_issuance.totalOrumIssued() / (10 ** 24)) == ceil(40 * (0.75 + (1 - 0.75)/2)) # 0.875
    # go one more year and trigger Orum issuance
    chain.mine(timedelta=365*86400)
    stability_pool.withdrawFromSP(Wei(10e18), {"from": alice})
    assert ceil(community_issuance.totalOrumIssued() / (10 ** 24)) == ceil(40 * (0.875 + (1 - 0.875)/2)) # 0.9375
    # go one more year and trigger Orum issuance
    chain.mine(timedelta=365*86400)
    stability_pool.withdrawFromSP(Wei(10e18), {"from": alice})
    assert ceil(community_issuance.totalOrumIssued() / (10 ** 24)) == ceil(40 * (0.9375 + (1 - 0.9375)/2)) # 0.96875
    # go one more year and trigger Orum issuance
    chain.mine(timedelta=365*86400)
    stability_pool.withdrawFromSP(Wei(10e18), {"from": alice})
    assert ceil(community_issuance.totalOrumIssued() / (10 ** 24)) == ceil(40 * (0.96875 + (1 - 0.96875)/2)) # 0.984375


