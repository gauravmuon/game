from enum import IntEnum

import brownie
from brownie import BufferBinaryOptions, OptionsConfig
from eth_account import Account
from eth_account.messages import encode_defunct

ONE_DAY = 86400


def to_32byte_hex(val):
    web3 = brownie.network.web3
    return web3.toHex(web3.toBytes(val).rjust(32, b"\0"))


class BinaryOptionTesting(object):
    def __init__(
        self,
        accounts,
        binary_options,
        binary_pool,
        total_fee,
        chain,
        tokenX,
        liquidity,
        period,
        is_above,
        router,
        publisher,
        settlement_fee_disbursal,
        binary_options_config,
        referral_contract,
        trader_nft_contract,
        creation_window,
        sf_publisher,
    ):
        self.settlement_fee_disbursal = settlement_fee_disbursal
        self.referral_contract = referral_contract
        self.trader_nft_contract = trader_nft_contract
        self.binary_options_config = binary_options_config
        self.publisher = publisher
        self.sf_publisher = sf_publisher
        self.binary_options = binary_options
        self.binary_pool = binary_pool
        self.total_fee = total_fee
        self.owner = accounts[0]
        self.user_1 = accounts[1]
        self.user_2 = accounts[2]
        self.bot = accounts[4]
        self.liquidity = liquidity
        self.tokenX = tokenX
        self.chain = chain
        self.period = period
        self.is_above = is_above
        self.router = router
        self.strike = int(400e8)
        self.slippage = 100
        self.allow_partial_fill = True
        self.sf = 1500
        self.params = [
            self.total_fee,
            self.period,
            self.is_above,
            self.binary_options.address,
            self.strike,
            self.slippage,
            self.allow_partial_fill,
            "",
            0,
        ]
        self.creation_window = creation_window
        self.trade_params = [
            self.total_fee,
            self.period,
            self.binary_options.address,
            self.strike,
            self.slippage,
            self.allow_partial_fill,
            "",
            0,
            int(398e8),
            15e2,
        ]

    def init(self):
        self.tokenX.approve(
            self.binary_pool.address, self.liquidity, {"from": self.owner}
        )
        self.binary_pool.provide(self.liquidity, 0, {"from": self.owner})
        self.router.setContractRegistry(self.binary_options.address, True)
        self.router.setInPrivateKeeperMode() if self.router.isInPrivateKeeperMode() else None

    def time_travel(self, day_of_week, hour, to_minute):
        # Get the current block timestamp
        current_timestamp = self.chain.time()

        # Calculate the timestamp for the specified day and hour
        current_day = ((current_timestamp / ONE_DAY) + 4) % 7
        if current_day < day_of_week:
            days_until_dow = day_of_week - current_day
        elif current_day > day_of_week:
            days_until_dow = 7 - current_day + day_of_week
        else:
            days_until_dow = 0
        target_timestamp = (
            current_timestamp
            + (days_until_dow * ONE_DAY)
            + (hour * 60 * 60)
            + (to_minute * 60)
        )
        # "Time travel" to the target timestamp
        self.chain.sleep(int(target_timestamp - current_timestamp))
        current_timestamp = self.chain.time()
        self.chain.mine(1)

    def check_trading_window(self, day, hour, min, period, expected):
        self.time_travel(day, hour, min)
        print(self.chain.time())
        assert (
            self.creation_window.isInCreationWindow(period) == expected
        ), f"Should {'' if expected else 'not'} be in creation window on {day} {hour}:{min} for period {period}"

    def verify_option_states(
        self,
        option_id,
        user,
        strike,
        expected_amount,
        expected_premium,
        expected_option_type,
        expected_total_fee,
        expected_settlement_fee,
        pool_balance_diff,
        sfd_diff,
        txn,
    ):
        (
            _,
            strike,
            amount,
            locked_amount,
            premium,
            _,
            _is_above,
            fee,
            _,
        ) = self.binary_options.options(option_id)

        assert self.binary_options.ownerOf(option_id) == user, "Wrong owner"
        print("settlmenr fee", sfd_diff, expected_settlement_fee)
        assert (
            txn.events["Create"]["settlementFee"] == expected_settlement_fee
            and sfd_diff == expected_settlement_fee
        ), "Wrong settlementFee"

        assert strike == strike, "Wrong strike"
        print(sfd_diff)
        print(amount, locked_amount, expected_amount)
        assert (
            amount == locked_amount == expected_amount
        ), "Wrong amount or locked amount"
        assert premium == expected_premium, "Wrong premium"
        assert _is_above == expected_option_type, "Wrong option_type"
        assert (
            fee == expected_total_fee - self.binary_options_config.platformFee()
        ), "Wrong fee"
        assert (
            self.tokenX.balanceOf(self.binary_options.address)
            == self.tokenX.balanceOf(self.router.address)
            == 0
        ), "Wrong option balance"
        assert pool_balance_diff == expected_premium, "Wrong premium transferred"
        assert (
            self.binary_pool.lockedLiquidity(self.binary_options.address, option_id)[0]
            == locked_amount
        ), "Wrong liquidity locked"
        assert txn.events["Save"], "Save event not emitted"

    def get_signature(self, token, timestamp, price, publisher=None):
        web3 = brownie.network.web3
        key = self.publisher.private_key if not publisher else publisher.private_key
        msg_hash = web3.solidityKeccak(
            ["string", "uint256", "uint256"],
            [BufferBinaryOptions.at(token).assetPair(), timestamp, int(price)],
        )
        signed_message = Account.sign_message(encode_defunct(msg_hash), key)

        return to_32byte_hex(signed_message.signature)

    def get_sf_signature(self, token, timestamp, sf_publisher=None):
        web3 = brownie.network.web3
        key = (
            self.sf_publisher.private_key
            if not sf_publisher
            else sf_publisher.private_key
        )
        msg_hash = web3.solidityKeccak(
            ["string", "uint256", "uint256"],
            [
                BufferBinaryOptions.at(token).assetPair(),
                timestamp,
                self.sf,
            ],
        )
        signed_message = Account.sign_message(encode_defunct(msg_hash), key)

        return to_32byte_hex(signed_message.signature)

    def get_close_signature(self, token, timestamp, optionId, publisher=None):
        web3 = brownie.network.web3
        key = self.publisher.private_key if not publisher else publisher.private_key
        msg_hash = web3.solidityKeccak(
            ["string", "uint256", "uint256"],
            [BufferBinaryOptions.at(token).assetPair(), timestamp, int(optionId)],
        )
        signed_message = Account.sign_message(encode_defunct(msg_hash), key)

        return to_32byte_hex(signed_message.signature)

    def get_user_signature(self, params, user, key):
        web3 = brownie.network.web3
        signature_time = self.chain.time()
        msg_hash = web3.solidityKeccak(
            [
                "address",
                "uint256",
                "uint256",
                "address",
                "uint256",
                "uint256",
                "bool",
                "string",
                "uint256",
                "uint256",
                "uint256",
            ],
            [user, *params, signature_time, self.sf],
        )
        signed_message = Account.sign_message(encode_defunct(msg_hash), key)

        return (to_32byte_hex(signed_message.signature), signature_time)

    def get_lo_user_signature(self, params, user, key):
        web3 = brownie.network.web3
        signature_time = self.chain.time()
        msg_hash = web3.solidityKeccak(
            [
                "address",
                "uint256",
                "uint256",
                "address",
                "uint256",
                "uint256",
                "bool",
                "string",
                "uint256",
                "uint256",
            ],
            [user, *params, signature_time],
        )
        signed_message = Account.sign_message(encode_defunct(msg_hash), key)

        return (to_32byte_hex(signed_message.signature), signature_time)

    def get_lo_user_signature_with_direction(
        self, params, is_above, user, signature_time, key
    ):
        web3 = brownie.network.web3
        msg_hash = web3.solidityKeccak(
            [
                "address",
                "uint256",
                "uint256",
                "address",
                "uint256",
                "uint256",
                "bool",
                "string",
                "uint256",
                "bool",
                "uint256",
            ],
            [user, *params, is_above, signature_time],
        )
        signed_message = Account.sign_message(encode_defunct(msg_hash), key)

        return (to_32byte_hex(signed_message.signature), signature_time)

    def get_user_signature_with_direction(
        self, params, is_above, user, signature_time, key
    ):
        web3 = brownie.network.web3
        msg_hash = web3.solidityKeccak(
            [
                "address",
                "uint256",
                "uint256",
                "address",
                "uint256",
                "uint256",
                "bool",
                "string",
                "uint256",
                "bool",
                "uint256",
                "uint256",
            ],
            [user, *params, is_above, signature_time, self.sf],
        )
        signed_message = Account.sign_message(encode_defunct(msg_hash), key)

        return (to_32byte_hex(signed_message.signature), signature_time)

    def get_user_signature_for_close(self, params, user, key):
        web3 = brownie.network.web3
        signature_time = self.chain.time()
        msg_hash = web3.solidityKeccak(
            ["address", "uint256", "address", "uint256"],
            [user, *params, signature_time],
        )
        signed_message = Account.sign_message(encode_defunct(msg_hash), key)

        return (to_32byte_hex(signed_message.signature), signature_time)

    def get_trade_params(self, user, one_ct, is_limit_order=False):
        sf_expiry = self.chain.time() + 3
        sf_signature = self.get_sf_signature(self.binary_options, sf_expiry)
        user_sign_info = (
            self.get_user_signature(
                self.trade_params[:8],
                user.address,
                one_ct.private_key,
            )
            if not is_limit_order
            else self.get_lo_user_signature(
                self.trade_params[:8], user.address, one_ct.private_key
            )
        )
        user_sign_info_for_execution = (
            self.get_user_signature_with_direction(
                self.trade_params[:8],
                self.is_above,
                user.address,
                user_sign_info[1],
                one_ct.private_key,
            )
            if not is_limit_order
            else self.get_lo_user_signature_with_direction(
                self.trade_params[:8],
                self.is_above,
                user.address,
                user_sign_info[1],
                one_ct.private_key,
            )
        )
        lo_expiration = self.chain.time() + ONE_DAY
        current_time = self.chain.time()
        trade_params = (
            [0, user]
            + self.trade_params
            + [is_limit_order, lo_expiration if is_limit_order else 0]
            + [
                [sf_signature, sf_expiry],
                user_sign_info,
                [
                    self.get_signature(
                        self.binary_options, current_time, self.trade_params[-2]
                    ),
                    current_time,
                ],
                user_sign_info_for_execution,
            ]
        )
        return trade_params

    def create(self, user, one_ct, is_limit_order=False):
        expected_option_id = self.binary_options.nextTokenId()
        trade_params = self.get_trade_params(user, one_ct, is_limit_order)
        txn = self.router.openTrades([trade_params[:-1]], {"from": self.bot})
        optionId = txn.events["OpenTrade"]["optionId"]
        queueId = txn.events["OpenTrade"]["queueId"]
        assert optionId == expected_option_id

        print(self.binary_options.options(optionId))
        return optionId, queueId, trade_params

    def unlock_options(self, options):
        params = []
        for option in options:
            option_data = self.binary_options.options(option[0])
            close_params = (self.binary_options.address, option_data[5], option[1])
            params.append(
                (
                    option[0],
                    *close_params,
                    self.get_signature(
                        *close_params,
                    ),
                )
            )
        txn = self.router.unlockOptions(
            params,
            {"from": self.bot},
        )
        return txn


def utility(contracts, accounts, chain):
    tokenX = contracts["tokenX"]
    binary_pool = contracts["binary_pool_atm"]
    router = contracts["router"]
    binary_options_config = contracts["binary_options_config_atm"]
    binary_options = contracts["binary_european_options_atm"]
    publisher = contracts["publisher"]
    sf_publisher = contracts["sf_publisher"]
    settlement_fee_disbursal = contracts["settlement_fee_disbursal"]
    referral_contract = contracts["referral_contract"]
    trader_nft_contract = contracts["trader_nft_contract"]
    creation_window = contracts["creation_window"]
    total_fee = int(1e6) + int(1e5)
    liquidity = int(1000000 * 1e6)
    period = 86300
    isAbove = False

    option = BinaryOptionTesting(
        accounts,
        binary_options,
        binary_pool,
        total_fee,
        chain,
        tokenX,
        liquidity,
        period,
        isAbove,
        router,
        publisher,
        settlement_fee_disbursal,
        binary_options_config,
        referral_contract,
        trader_nft_contract,
        creation_window,
        sf_publisher,
    )
    option.init()

    return option
