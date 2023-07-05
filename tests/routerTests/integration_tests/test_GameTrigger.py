#!/usr/bin/python3

import brownie
import pytest
import time
from eth_account import Account
from eth_account.messages import encode_defunct
import helpers

# private function should not exist
# accessing them must produce attribute error
def test_game_trigger(upVsDownGameV2, router, accounts, ether, irrevelent_num, ADMIN, KEEPER, DEFAULT_ADMIN):

  PUBLISHER = OWNER = DEFAULT_ADMIN

  helpers.start_game_and_create_pool(upVsDownGameV2, ether, ADMIN, DEFAULT_ADMIN)

  router.setContractRegistry(upVsDownGameV2.address, True, {"from":accounts[0]})
  router.setKeeper(KEEPER, True, {"from":DEFAULT_ADMIN})
  assert router.isKeeper(KEEPER)

  TRADER_1 = accounts.add()
  TRADER_2 = accounts.add()
  print(TRADER_1,TRADER_2)

  trigger_params = {
    "poolId": bytes(1),
    "timeMS": time.time_ns(),
    "tradesStartTimeMS": time.time_ns() + 10_000,
    "tradesEndTimeMS": time.time_ns() + 20_000,
    "price": 11,
    "batchSize": 11,
    "targetContract": 11,
  }

  trade_1_msg = brownie.web3.solidityKeccak(
    ["string",""],
    list(trigger_params.values())
  )

  trade_1_sign = Account.sign_message(encode_defunct(trade_1_msg), TRADER_1.private_key)
  trade_1_signature = helpers.to_32byte_hex(trade_1_sign.signature)
  
  trigger_params["targetContract"] = upVsDownGameV2.address
  trigger_params["publisherSignature"] = trade_1_signature
  trigger_params["publisherSignatureTimestamp"] = time.time()

  trade_1_placed = router.openTrades([tuple(trigger_params.values())], {"from":KEEPER})
  print(str(trade_1_placed.return_value))
  print(str(trade_1_placed.events))


