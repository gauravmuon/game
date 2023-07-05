# #!/usr/bin/python3

# import brownie
# import pytest
# import time
# from eth_account import Account
# from eth_account.messages import encode_defunct

# # mind in accounts address 0 is owner and address 1 is game controller

# # this is a helper function
# def to_32byte_hex(val):
#   web3 = brownie.web3
#   return web3.toHex(web3.toBytes(val).rjust(32, b"\0"))

# # private function should not exist
# # accessing them must produce attribute error
# def test_signed_msg(upVsDownGameV2, router, accounts, ether, irrevelent_num):
#   ADMIN = accounts[1]
#   PUBLISHER = OWNER = DEFAULT_ADMIN = accounts[0]
#   KEEPER = accounts[2]

#   # starting the game by owner account
#   game_started = upVsDownGameV2.startGame({"from": accounts[0]})
#   pool_1_args = {
#       "poolId" : bytes(1), 
#       "minBetAmount" : 5*ether, 
#       "maxBetAmount" : 100*ether, 
#       "poolBetsLimit" : 5 # number of members allowed in up and down pool
#   }

#   # creating a pool by game admint
#   pool_1 = upVsDownGameV2.createPool(
#       *list(pool_1_args.values()), 
#       {"from": ADMIN}
#   )

#   router.setContractRegistry(upVsDownGameV2.address, True, {"from":accounts[0]})
#   router.setKeeper(KEEPER, True, {"from":DEFAULT_ADMIN})
#   assert router.isKeeper(KEEPER)

#   TRADER_1 = accounts.add()
#   TRADER_2 = accounts.add()
#   print(TRADER_1,TRADER_2)

#   trade_1_params = {
#     "poolId": bytes(1),
#     "queueId": 1,
#     "avatarUrl": "avatar_1",
#     "countryCode": "IN",
#     "upOrDown": True,
#     "whiteLabelId": "id_1",
#     "trader": TRADER_1.address,
#   }

#   trade_1_msg = brownie.web3.solidityKeccak(
#     ["bytes","uint256", "string", "string", "bool", "string", "address"],
#     list(trade_1_params.values())
#   )

#   trade_1_sign = Account.sign_message(encode_defunct(trade_1_msg), TRADER_1.private_key)
#   trade_1_signature = to_32byte_hex(trade_1_sign.signature)
  
#   trade_1_params["signature"] = trade_1_signature
#   trade_1_params["signatureTimestamp"] = time.time()
#   trade_1_params["targetContract"] = upVsDownGameV2.address

#   trade_1_placed = router.openTrades([tuple(trade_1_params.values())], {"from":KEEPER})
#   print(str(trade_1_placed.return_value))
#   print(str(trade_1_placed.events))


