from brownie import Wei, chain

def test_orum_initial_issuance(isolation, eren, OrumToken, YuzuPool, YuzuLP, CommunityIssuance):
    # Get the latest deployed contracts
    orum_token = OrumToken[-1]
    yuzu_pool = YuzuPool[-1]
    community_issuance = CommunityIssuance[-1]
    # Check if the yuzu pool contract, community issuance, multisig address, and lockup factory contract have been issued 
    # Orum tokens
    orum_community_issuance_balance = orum_token.balanceOf(community_issuance.address)
    orum_yuzu_pool_balance = orum_token.balanceOf(yuzu_pool.address)
    orum_eren_balance = orum_token.balanceOf(eren.address)
    assert orum_yuzu_pool_balance == Wei(5 * 10**24)
    assert orum_community_issuance_balance == Wei(40 * 10**24)
    assert orum_eren_balance == Wei(55 * 10**24)
    assert orum_community_issuance_balance + orum_yuzu_pool_balance + orum_eren_balance == Wei(10**26)

def test_yuzu_lp_staking_to_farm_orum(isolation, katy,lauren, OrumToken, YuzuPool, YuzuLP):
    # get the latest deployed contracts
    yuzu_pool = YuzuPool[-1]
    yuzu_lp = YuzuLP[-1]
    orum_token = OrumToken[-1]
    # Mint yuzu lp tokens for alice and bob
    yuzu_lp.mint(katy.address, 1000, {"from": katy})
    yuzu_lp.mint(lauren.address, 1500, {"from": lauren})
    # calculate the initial orum token balance of katy and lauren
    katy_orum_balance_init = orum_token.balanceOf(katy)
    lauren_orum_balance_init = orum_token.balanceOf(lauren)
    # approve yuzu pool to use katy and lauren's lp tokens for staking
    yuzu_lp.approve(yuzu_pool.address, 900, {"from": katy})
    yuzu_lp.approve(yuzu_pool.address, 1200, {"from": lauren})
    # alice and bob stake their lp tokens in the yuzu pool contract
    yuzu_pool.stake(900, {"from": katy})
    yuzu_pool.stake(1200, {"from": lauren})
    # time-travel 1 week into the future and claim orum tokens
    chain.mine(timedelta=7*86400)
    yuzu_pool.claimReward({"from": katy})
    yuzu_pool.claimReward({"from": lauren})
    # check if the orum balance of both katy and lauren has increased
    assert orum_token.balanceOf(katy) > katy_orum_balance_init
    assert orum_token.balanceOf(lauren) > lauren_orum_balance_init

