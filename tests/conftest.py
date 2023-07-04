#!/usr/bin/python3

import time
from enum import IntEnum

import pytest

ONE_DAY = 86400


class OptionType(IntEnum):
    ALL = 0
    PUT = 1
    CALL = 2
    NONE = 3


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass

@pytest.fixture(scope="module")
def upVsDownGameV2(UpVsDownGameV2, accounts):
    # address 0 will be owner ie (msg.sender), and 1 will be admin
    return UpVsDownGameV2.deploy(accounts[1], "UpVsDownGameV2", {'from': accounts[0]})
    
@pytest.fixture(scope="module")
def router(Router, accounts):
    return Router.deploy(accounts[1], accounts[0], {'from': accounts[0]})

@pytest.fixture
def ether():
   return 1e18

@pytest.fixture
def irrevelent_num():
   return 1

@pytest.fixture(scope="module")
def contracts(
    accounts,
    USDC,
    BFR,
    BufferBinaryPool,
    BufferBinaryOptions,
    OptionsConfig,
    BufferRouter,
    FakeTraderNFT,
    ReferralStorage,
    SettlementFeeDistributorV2,
    CreationWindow,
    LBFR,
    ABDKMath64x64,
    OptionMath,
    Validator,
    FaucetLBFR,
    PoolOIConfig,
    PoolOIStorage,
    OptionStorage,
    MarketOIConfig,
):
    publisher = accounts.add()
    sf_publisher = accounts.add()
    admin = accounts.add()
    ibfr_contract = BFR.deploy({"from": accounts[0]})
    sfd = accounts.add()
    tokenX = USDC.deploy({"from": accounts[0]})
    ABDKMath64x64.deploy({"from": accounts[0]})
    OptionMath.deploy({"from": accounts[0]})
    Validator.deploy({"from": accounts[0]})

    creation_window = CreationWindow.deploy(
        1682269200, 1682701200, {"from": accounts[0]}
    )
    binary_pool_atm = BufferBinaryPool.deploy(
        tokenX.address, 600, {"from": accounts[0]}
    )
    OPTION_ISSUER_ROLE = binary_pool_atm.OPTION_ISSUER_ROLE()
    router = BufferRouter.deploy(publisher, sf_publisher, admin, {"from": accounts[0]})
    trader_nft = FakeTraderNFT.deploy(accounts[9], {"from": accounts[0]})

    print("############### Binary ATM Options 1 #################")
    binary_options_config_atm = OptionsConfig.deploy(
        binary_pool_atm.address,
        {"from": accounts[0]},
    )
    referral_contract = ReferralStorage.deploy({"from": accounts[0]})

    binary_european_options_atm = BufferBinaryOptions.deploy(
        tokenX.address,
        binary_pool_atm.address,
        binary_options_config_atm.address,
        referral_contract.address,
        1,
        "ETH",
        "BTC",
        {"from": accounts[0]},
    )
    market_oi_config = MarketOIConfig.deploy(
        10e6, 2e6, binary_european_options_atm.address, {"from": accounts[0]}
    )
    option_storage = OptionStorage.deploy({"from": accounts[0]})
    pool_oi_storage = PoolOIStorage.deploy({"from": accounts[0]})
    pool_oi_config = PoolOIConfig.deploy(
        12e6, pool_oi_storage.address, {"from": accounts[0]}
    )

    binary_options_config_atm.setSettlementFeeDisbursalContract(
        sfd,
        {"from": accounts[0]},
    )
    binary_options_config_atm.setCreationWindowContract(
        creation_window.address, {"from": accounts[0]}
    )

    binary_european_options_atm.approvePoolToTransferTokenX(
        {"from": accounts[0]},
    )
    binary_pool_atm.grantRole(
        OPTION_ISSUER_ROLE,
        binary_european_options_atm.address,
        {"from": accounts[0]},
    )
    ROUTER_ROLE = binary_european_options_atm.ROUTER_ROLE()
    UPDATOR_ROLE = pool_oi_storage.UPDATOR_ROLE()
    binary_european_options_atm.grantRole(
        ROUTER_ROLE,
        router.address,
        {"from": accounts[0]},
    )
    pool_oi_storage.grantRole(
        UPDATOR_ROLE,
        binary_european_options_atm.address,
        {"from": accounts[0]},
    )

    # binary_options_config_atm.settraderNFTContract(trader_nft.address)
    binary_european_options_atm.setConfigure([2, 4, 6, 8], {"from": accounts[0]})

    # bfr_binary_options_config_atm.settraderNFTContract(trader_nft.address)
    referral_contract.setConfigure([2, 4, 6], [25e3, 50e3, 75e3], {"from": accounts[0]})

    lbfr = LBFR.deploy({"from": accounts[0]})
    faucet_lbfr = FaucetLBFR.deploy(lbfr.address, publisher, {"from": accounts[0]})

    MINTER_ROLE = lbfr.MINTER_ROLE()
    lbfr.grantRole(
        MINTER_ROLE,
        faucet_lbfr.address,
        {"from": accounts[0]},
    )
    binary_options_config_atm.setOptionStorageContract(option_storage.address)
    binary_options_config_atm.setPoolOIStorageContract(pool_oi_storage.address)
    binary_options_config_atm.setMarketOIConfigContract(market_oi_config.address)
    binary_options_config_atm.setPoolOIConfigContract(pool_oi_config.address)
    binary_options_config_atm.setIV(1100)

    binary_european_options_atm_2 = BufferBinaryOptions.deploy(
        tokenX.address,
        binary_pool_atm.address,
        binary_options_config_atm.address,
        referral_contract.address,
        1,
        "ETH",
        "USD",
        {"from": accounts[0]},
    )
    return {
        "tokenX": tokenX,
        "referral_contract": referral_contract,
        "binary_pool_atm": binary_pool_atm,
        "binary_options_config_atm": binary_options_config_atm,
        "binary_european_options_atm": binary_european_options_atm,
        "router": router,
        "trader_nft_contract": trader_nft,
        "ibfr_contract": ibfr_contract,
        "publisher": publisher,
        "settlement_fee_disbursal": sfd,
        "settlement_fee_disbursal_v2": SettlementFeeDistributorV2,
        "creation_window": creation_window,
        "lbfr": lbfr,
        "faucet_lbfr": faucet_lbfr,
        "lbfr": lbfr,
        "binary_european_options_atm_2": binary_european_options_atm_2,
        "sf_publisher": sf_publisher,
    }
