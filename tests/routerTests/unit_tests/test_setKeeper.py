#!/usr/bin/python3

import helpers

def test_keepers(upVsDownGameV2, router, accounts, 
                    ether, ADMIN, DEFAULT_ADMIN, KEEPER):

  helpers.start_game_and_create_pool(upVsDownGameV2, ether, ADMIN, DEFAULT_ADMIN)

  assert router.isKeeper(KEEPER) == False
  router.setKeeper(KEEPER, True, {"from":DEFAULT_ADMIN})
  assert router.isKeeper(KEEPER) == True
  
  assert router.isKeeper(accounts[5].address) == False
  router.setKeeper(accounts[5].address, True, {"from":DEFAULT_ADMIN})
  assert router.isKeeper(accounts[5].address) == True
  router.setKeeper(accounts[5].address, False, {"from":DEFAULT_ADMIN})
  assert router.isKeeper(accounts[5].address) == False

  router.setKeeper(accounts[6].address, True, {"from":DEFAULT_ADMIN})
  assert router.isKeeper(accounts[6].address) == True

  router.setKeeper(accounts[6].address, False, {"from":DEFAULT_ADMIN})
  assert router.isKeeper(accounts[6].address) == False
  router.setKeeper(accounts[6].address, True, {"from":DEFAULT_ADMIN})
  assert router.isKeeper(accounts[6].address) == True