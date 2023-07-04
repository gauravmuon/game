import time
import functools

# this not test case but helper, it is used for starting and ending the first round
def complete_first_round(upVsDownGameV2, accounts, ether, irrevelent_num):
    # starting the game by owner account
    game_started = upVsDownGameV2.startGame({"from": accounts[0]})
    pool_1_args = {
        "poolId" : bytes(1), 
        "minBetAmount" : 5*ether, 
        "maxBetAmount" : 100*ether, 
        "poolBetsLimit" : 5 # number of members allowed in up and down pool
    }
    # creating a pool by game controller account
    pool_1 = upVsDownGameV2.createPool(
        *list(pool_1_args.values()), 
        {"from": accounts[1]}
    )

    round_1_args_start = {
        "poolId": bytes(1),
        "timeMS": time.time(),
        "tradesStartTimeMS": time.time(),
        "tradesEndTimeMS": time.time() + 10,
        "price": 300,
        "batchSize": irrevelent_num
    }
    round_1_started = upVsDownGameV2.trigger(*round_1_args_start.values(), {"from": accounts[1]})

    round_2_args_end = {
        "poolId": bytes(1),
        "timeMS": time.time() + 10,
        "tradesStartTimeMS": time.time() + 10,
        "tradesEndTimeMS": time.time() + 10,
        "price": 400,
        "batchSize": 0
    }
    round_1_ended = upVsDownGameV2.trigger(*round_2_args_end.values(), {"from": accounts[1]})

    # confirm if no pending distributions
    has_pending_distribution = upVsDownGameV2.hasPendingDistributions(bytes(1))
    assert has_pending_distribution == False
    return {
        "game_started":game_started,
        "pool_1":pool_1,
        "pool_1_args":pool_1_args,
        "round_1_started":round_1_started,
        "round_1_ended":round_1_ended,
    }



# mind, use int calculation for producing the exact result as in solidity
# python follows float point calculation, be alert
def calculate_winnings(upVsDownGameV2, accounts, trade_id_amount, winners_list):

    # structure of
    # trade_id_amount = {
    #     # id : (amount_to_bet, is_winner, account_index)
    #     "id1": (10*ether, False, 4),
    #     "id2": (5*ether, True, 5),
    # }

    fee_percentage = upVsDownGameV2.feePercentage()
    winners_bet_amount = 0 # winners total amount

    for winner_id in winners_list:
        winners_bet_amount += trade_id_amount[winner_id][0]

    total_amount = functools.reduce(lambda prv, curr: prv + curr, [x[0] for x in trade_id_amount.values()], 0)
    total_amount -= winners_bet_amount # total amount after deducting winners total amount

    game_fees = int(int(total_amount * fee_percentage)/100)
    remaining_amount = int(total_amount - game_fees) # total amount after deducting game fees

    result = {} 
    for winner_id in winners_list:
        result[winner_id] = ((int((trade_id_amount[winner_id][0] * 100) / winners_bet_amount) 
                              * remaining_amount)/100)
    print(str(result))
    return result