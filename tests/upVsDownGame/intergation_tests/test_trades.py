#!/usr/bin/python3

import brownie
import pytest
import time
import helpers

# mind, in accounts address 0 is owner and address 1 is game controller
# and first round will always be dummy round

# one trader should win in the second round out of two,
# because one is betting up and other is down
# this testcase syncs delay as same on the blockchain
def test_trade_with_delay_sync(upVsDownGameV2, accounts, ether, irrevelent_num):

    # starting the game by owner account
    game_started = upVsDownGameV2.startGame({"from": accounts[0]})
    # creating a pool by game controller account
    pool_1 = upVsDownGameV2.createPool(
        bytes(1), 5*ether, 50*ether, 50*ether, {"from": accounts[1]})

    round_1_started = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time()+10, time.time()+20, 300, irrevelent_num, {"from": accounts[1]})

    time.sleep(10)  # delay for syncing block.timestamp on blockchain

    round_1_ended = upVsDownGameV2.trigger(bytes(1), time.time(), time.time(
    )+30, time.time()+40, 400, 0, {"from": accounts[1]})

    time.sleep(5)  # delay for syncing block.timestamp on blockchain

    # doing some trades
    # should win
    trade_1 = upVsDownGameV2.makeTrade(
        list({
            "poolId": bytes(1),
            "avatarUrl": "avatar_1",
            "countryCode": "IN",
            "upOrDown": True,
            "whiteLabelId": "id_1",
            "trader": accounts[5]
        }.values()),
        {"from": accounts[5], "value": 10*ether}
    )
    print("trade 1:" + str(trade_1.events))

    # should lose
    trade_2 = upVsDownGameV2.makeTrade(
        list({
            "poolId": bytes(1),
            "avatarUrl": "avatar_2",
            "countryCode": "IN",
            "upOrDown": False,
            "whiteLabelId": "id_2",
            "trader": accounts[6],
        }.values()),
        {"from": accounts[6], "value": 5*ether}
    )
    print("trade 2:" + str(trade_2.events))

    time.sleep(15)  # delay for syncing block.timestamp on blockchain

    round_2_started = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time()+10, time.time()+20, 300, irrevelent_num, {"from": accounts[1]})

    round_2_ended = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time()+30, time.time()+40, 400, 1, {"from": accounts[1]})

    print(str(round_2_ended.events))

    assert (len(round_2_ended.events["TradeWinningsSent"]) == 1)
    assert (round_2_ended.events["TradeWinningsSent"]
            [0]["winningsAmount"] == 4.75*ether)
    assert (len(round_2_ended.events["RoundDistributed"]) == 1)
    assert (round_2_ended.events["RoundDistributed"][0]["totalWinners"] == 1)


# one trader should win in the second round out of two,
# because one is betting up and other is down
def test_trade_fast_forward(upVsDownGameV2, accounts, ether, irrevelent_num):

    helpers.complete_first_round(
        upVsDownGameV2,
        accounts,
        ether,
        irrevelent_num
    )

    # doing some trades
    # should win
    trade_1 = upVsDownGameV2.makeTrade(
        list({
            "poolId": bytes(1),
            "avatarUrl": "avatar_1",
            "countryCode": "IN",
            "upOrDown": True,
            "whiteLabelId": "id_1",
            "trader":accounts[5]
        }.values()),
        {"from": accounts[5], "value": 10*ether}
    )
    print("trade 1:" + str(trade_1.events))

    # should loose
    trade_2 = upVsDownGameV2.makeTrade(
        list({
            "poolId": bytes(1),
            "avatarUrl": "avatar_2",
            "countryCode": "IN",
            "upOrDown": False,
            "whiteLabelId": "id_2",
            "trader":accounts[6]
        }.values()),
        {"from": accounts[6], "value": 5*ether}
    )
    print("trade 2:" + str(trade_2.events))

    round_2_started = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time(), time.time() + 10, 300, irrevelent_num, {"from": accounts[1]})

    round_2_ended = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time(), time.time() + 10, 400, 1, {"from": accounts[1]})

    print(str(round_2_ended.events))

    assert (len(round_2_ended.events["TradeWinningsSent"]) == 1)
    assert (round_2_ended.events["TradeWinningsSent"]
            [0]["winningsAmount"] == 4.75*ether)
    assert (len(round_2_ended.events["RoundDistributed"]) == 1)
    assert (round_2_ended.events["RoundDistributed"][0]["totalWinners"] == 1)


# no traders should win in this test case, rather trades should be returned
# # because up pool have two players and down pool will have zero
def test_trade_no_winnigs_as_all_up(upVsDownGameV2, accounts, ether, irrevelent_num):

    helpers.complete_first_round(
        upVsDownGameV2,
        accounts,
        ether,
        irrevelent_num
    )

    # doing some trades
    trade_1 = upVsDownGameV2.makeTrade(
        list({
            "poolId": bytes(1),
            "avatarUrl": "avatar_1",
            "countryCode": "IN",
            "upOrDown": True,
            "whiteLabelId": "id_1",
            "trader":accounts[5]
        }.values()),
        {"from": accounts[5], "value": 10*ether}
    )
    print("trade 1:" + str(trade_1.events))

    trade_2 = upVsDownGameV2.makeTrade(
        list({
            "poolId": bytes(1),
            "avatarUrl": "avatar_2",
            "countryCode": "IN",
            "upOrDown": True,
            "whiteLabelId": "id_2",
            "trader":accounts[6]
        }.values()),
        {"from": accounts[6], "value": 5*ether}
    )
    print("trade 2:" + str(trade_2.events))

    has_pending_distribution = upVsDownGameV2.hasPendingDistributions(bytes(1))
    assert has_pending_distribution

    round_2_started = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time(), time.time() + 10, 300, irrevelent_num, {"from": accounts[1]})

    has_pending_distribution = upVsDownGameV2.hasPendingDistributions(bytes(1))
    assert has_pending_distribution

    round_2_ended = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time(), time.time() + 10, 400, 2, {"from": accounts[1]})

    print(str(round_2_ended.events))

    # should be equals to the total participants
    assert len(round_2_ended.events["TradeReturned"]) == 2

    # should get the full bet amount back
    assert round_2_ended.events["TradeReturned"][0]["amount"] == 10*ether
    assert round_2_ended.events["TradeReturned"][1]["amount"] == 5*ether
    # there will be two winners as nobody won
    assert round_2_ended.events["RoundDistributed"][0]["totalWinners"] == 2


# no traders should win in this test case, rather trades should be returned
# # because down pool have two players and up pool will zero
def test_trade_no_winnigs_as_all_down(upVsDownGameV2, accounts, ether, irrevelent_num):

    helpers.complete_first_round(
        upVsDownGameV2,
        accounts,
        ether,
        irrevelent_num
    )

    # doing some trades
    trade_1 = upVsDownGameV2.makeTrade(
        list({
            "poolId": bytes(1),
            "avatarUrl": "avatar_1",
            "countryCode": "IN",
            "upOrDown": False,
            "whiteLabelId": "id_1",
            "trader":accounts[5]
        }.values()),
        {"from": accounts[5], "value": 10*ether}
    )
    print("trade 1:" + str(trade_1.events))

    trade_2 = upVsDownGameV2.makeTrade(
        list({
            "poolId": bytes(1),
            "avatarUrl": "avatar_2",
            "countryCode": "IN",
            "upOrDown": False,
            "whiteLabelId": "id_2",
            "trader":accounts[6]
        }.values()),
        {"from": accounts[6], "value": 5*ether}
    )
    print("trade 2:" + str(trade_2.events))

    round_2_started = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time(), time.time() + 10, 300, irrevelent_num, {"from": accounts[1]})

    has_pending_distribution = upVsDownGameV2.hasPendingDistributions(bytes(1))
    assert has_pending_distribution

    round_2_ended = upVsDownGameV2.trigger(bytes(1), time.time(
    ), time.time(), time.time() + 10, 400, 2, {"from": accounts[1]})

    print(str(round_2_ended.events))

    # should be equals to the total participants
    assert len(round_2_ended.events["TradeReturned"]) == 2

    # should get the full bet amount back
    assert round_2_ended.events["TradeReturned"][0]["amount"] == 10*ether
    assert round_2_ended.events["TradeReturned"][1]["amount"] == 5*ether
    # there will be two winners as nobody won
    assert round_2_ended.events["RoundDistributed"][0]["totalWinners"] == 2
