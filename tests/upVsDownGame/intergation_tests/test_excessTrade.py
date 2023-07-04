#!/usr/bin/python3

import brownie
import pytest
import time
import helpers


# checking the allowed limit trade boundry
def test_trade_more_than_allowed_limit(upVsDownGameV2, accounts, ether, irrevelent_num):

    round_init = helpers.complete_first_round(
        upVsDownGameV2,
        accounts,
        ether,
        irrevelent_num
    )

    try:
        # trading more than allowed limit(100 ethers) should crash the call
        trade_1 = upVsDownGameV2.makeTrade(
            list({
                "poolId": bytes(1),
                "avatarUrl": "avatar_1",
                "countryCode": "IN",
                "upOrDown": True,
                "whiteLabelId": "id_1",
                "trader": accounts[5], 
            }.values()),
            {
                "from": accounts[5], 
                "value": round_init["pool_1_args"]["maxBetAmount"] + 1*ether
            }
        )
        assert False
    except brownie.exceptions.VirtualMachineError:
        pass


# checking the allowed limit trade boundry
def test_trade_allowed_members_limit(upVsDownGameV2, accounts, ether, irrevelent_num):

    round_init = helpers.complete_first_round(
        upVsDownGameV2,
        accounts,
        ether,
        irrevelent_num
    )
    # trying to add number of trades plus one extra than allowed
    # this should generate VirtualMachineError 
    try:
        for x in range(round_init["pool_1_args"]["poolBetsLimit"]+1):
            minAmount = round_init["pool_1_args"]["minBetAmount"]
            trade = upVsDownGameV2.makeTrade(
                list({
                    "poolId": bytes(1),
                    "avatarUrl": "avatar_1",
                    "countryCode": "IN",
                    "upOrDown": True,
                    "whiteLabelId": "id_"+str(x),
                    "trader": accounts[5], 
                }.values()),
                {
                    "from": accounts[int(x%10)], # using accounts between 0 to 9
                    "value": minAmount
                }
            )
        assert False
    except brownie.exceptions.VirtualMachineError:
        pass


