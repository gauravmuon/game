#!/usr/bin/python3

import brownie
import pytest
import time
import helpers


# this function is used for converting `trade_id_amount` dict to actual txns
def _helper_big_trade(upVsDownGameV2, accounts, ether, irrevelent_num, trade_id_amount):

    # structure of
    # trade_id_amount = {
    #     # id : (amount_to_bet, is_winner, account_index)
    #     "id1": (10*ether, False, 4),
    #     "id2": (5*ether, True, 5),
    #     "id3": (50*ether, True, 6),
    # }

    round_init = helpers.complete_first_round(
        upVsDownGameV2,
        accounts,
        ether,
        irrevelent_num
    )

    # dictionary for storing the inital balance of account
    original_amt_before_trade = {} # {"id1":33*ether, "id2":10*ether, ...etc}
    winners_list = []  # will hold the ids of winner account ["id2","id3"..etc]
    type_of_bools_used = set() # can become [True, False]

    for id in trade_id_amount:
        # pushing True or Flase (is winner) value, 
        # for determining up and down pools emptyness
        type_of_bools_used.add(trade_id_amount[id][1])
        
        # storing the initial amt of engaged accounts
        original_amt_before_trade[id] = accounts[trade_id_amount[id][2]].balance()

        make_trade_args = {
            "poolId": bytes(1),
            "avatarUrl": "avatar_"+id,
            "countryCode": "IN",
            "upOrDown": not trade_id_amount[id][1],
            "whiteLabelId": id,
            "trader": accounts[trade_id_amount[id][2]]
        }
        # converting the trade_id_amount dict in actual txn
        upVsDownGameV2.makeTrade(
            list(make_trade_args.values()),
            {"from": accounts[trade_id_amount[id][2]],
                "value": trade_id_amount[id][0]}
        )
        if trade_id_amount[id][1] == True:
            # if account is set to be winners
            winners_list.append(id)

    # check if both up and down pools have members
    if len(type_of_bools_used) == 2:
        # calculating the price, which will be distribute by the game contract
        winnings_list = helpers.calculate_winnings(
            upVsDownGameV2,
            accounts,
            trade_id_amount,
            winners_list
        )
    else:
        # only one pool have members
        winners_list = [x for x in trade_id_amount]
        # everyone will be counted as winner now
        for x in trade_id_amount:
            # overwriting the incoming tuple with all as True
            trade_id_amount[x] = (trade_id_amount[x][0],
                                  True, trade_id_amount[x][2])
        # generating the id dict of winners with winning amount equals to 0
        winnings_list = {x: 0 for x in trade_id_amount}

    # ========= starting the second round and closing it ================
    round_2_args_start = {
        "poolId": bytes(1),
        "timeMS": time.time(),
        "tradesStartTimeMS": time.time(),
        "tradesEndTimeMS": time.time() + 10,
        "price": 300,
        "batchSize": irrevelent_num
    }
    round_2_args_end = {
        "poolId": bytes(1),
        "timeMS": time.time(),
        "tradesStartTimeMS": time.time(),
        "tradesEndTimeMS": time.time() + 10,
        "price": 200,
        "batchSize": len(winners_list)
    }
    round_2_started = upVsDownGameV2.trigger(
        *round_2_args_start.values(),
        {"from": accounts[1]}
    )
    round_2_ended = upVsDownGameV2.trigger(
        *round_2_args_end.values(),
        {"from": accounts[1]}
    )

    # check if both up and down pools have members, 
    # type of bool should be [True, False]
    if len(type_of_bools_used) == 2:
        # confirming winners count, using events logs
        assert (
            len(round_2_ended.events["TradeWinningsSent"]) == len(winners_list))
        # validating the distribute amount price, with the calculated price
        for i in range(len(winners_list)):
            assert (round_2_ended.events["TradeWinningsSent"][i]["winningsAmount"]
                    == winnings_list[winners_list[i]])
    else:
        # should be equals to the total participants
        assert len(round_2_ended.events["TradeReturned"]) == len(winners_list)

    # validating balance of the non winner traders
    for id in trade_id_amount:
        if not trade_id_amount[id][1]:
            assert (accounts[trade_id_amount[id][2]].balance() ==
                    original_amt_before_trade[id] - trade_id_amount[id][0])

    # validating the accounts balance, after winning the bet
    for id in winnings_list:
        assert (accounts[trade_id_amount[id][2]].balance() ==
                winnings_list[id] + original_amt_before_trade[id])

    assert (len(round_2_ended.events["RoundDistributed"]) == 1)
    assert (round_2_ended.events["RoundDistributed"][0]["totalWinners"]
            == len(winners_list))


# one trader should win in the second round out of 6 traders
def test_big_trade_1(upVsDownGameV2, accounts, ether, irrevelent_num):

    trade_id_amount = {
        # id : {amount_to_bet, is_winner, account_index}
        "id1": (10*ether, False, 4),
        "id2": (5*ether, True, 5),
        "id3": (50*ether, True, 6),
        "id4": (10*ether, False, 7),
        "id5": (25*ether, False, 8),
        "id6": (30*ether, False, 9)
    }
    _helper_big_trade(upVsDownGameV2, accounts, ether,irrevelent_num, trade_id_amount)


def test_big_trade_2(upVsDownGameV2, accounts, ether, irrevelent_num):

    trade_id_amount = {
        # id : {amount_to_bet, is_winner, account_index}
        "id1": (10*ether, True, 4),
        "id2": (5*ether, False, 5),
        "id3": (50*ether, True, 6),
        "id4": (10*ether, True, 7),
        "id5": (25*ether, True, 8),
        "id6": (30*ether, True, 9)
    }
    _helper_big_trade(upVsDownGameV2, accounts, ether, irrevelent_num, trade_id_amount)


@pytest.mark.parametrize("idx", range(0, 3))
def test_big_trade_3(upVsDownGameV2, accounts, ether, irrevelent_num, idx):

    trade_id_amount = {
        # id : {amount_to_bet, is_winner, account_index}
        "id1": (10*ether, True, idx + 4),
        "id2": (25*ether, False, idx + 5),
        "id3": (50*ether, True, idx + 6),
        "id4": (10*ether, True, idx + 7),
    }
    _helper_big_trade(upVsDownGameV2, accounts, ether, irrevelent_num, trade_id_amount)


# no traders should win in this test case, rather trades should be returned
# # because up pool have two players and down pool will have zero
def test_trade_no_winnigs_as_all_up(upVsDownGameV2, accounts, ether, irrevelent_num):

    trade_id_amount = {
        # id : {amount_to_bet, is_winner, account_index}
        "id1": (10*ether, False, 4),
        "id2": (25*ether, False, 5),
        "id3": (50*ether, False, 6),
        "id4": (55*ether, False, 7),
        "id4": (85*ether, False, 8),
    }
    _helper_big_trade(upVsDownGameV2, accounts, ether, irrevelent_num, trade_id_amount)


# no traders should win in this test case, rather trades should be returned
# # because up pool have two players and down pool will have zero
def test_trade_no_winnigs_as_all_down(upVsDownGameV2, accounts, ether, irrevelent_num):

    trade_id_amount = {
        # id : {amount_to_bet, is_winner, account_index}
        "id1": (10*ether, True, 4),
        "id2": (25*ether, True, 5),
        "id3": (50*ether, True, 6),
        "id4": (10*ether, True, 7),
        "id4": (70*ether, True, 8),
        "id4": (50*ether, True, 9),
    }
    _helper_big_trade(upVsDownGameV2, accounts, ether, irrevelent_num, trade_id_amount)
