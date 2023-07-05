from brownie import web3

def start_game_and_create_pool(upVsDownGameV2, ether, ADMIN, DEFAULT_ADMIN):
  # starting the game by owner account
  game_started = upVsDownGameV2.startGame({"from": DEFAULT_ADMIN})
  pool_1_args = {
      "poolId" : bytes(1), 
      "minBetAmount" : 5*ether, 
      "maxBetAmount" : 100*ether, 
      "poolBetsLimit" : 5 # number of members allowed in up and down pool
  }

  # creating a pool by game admint
  pool_1 = upVsDownGameV2.createPool(
      *list(pool_1_args.values()), 
      {"from": ADMIN}
  )

  return {
    "game_starte":game_started,
    "pool_1_args":pool_1_args,
    "pool_1":pool_1,
  }
