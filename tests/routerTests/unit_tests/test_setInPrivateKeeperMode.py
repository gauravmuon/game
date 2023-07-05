#!/usr/bin/python3

import helpers

def test_private_keeper_mode(upVsDownGameV2, router, accounts, 
                    ether, ADMIN, DEFAULT_ADMIN):

  helpers.start_game_and_create_pool(upVsDownGameV2, ether, ADMIN, DEFAULT_ADMIN)

  assert router.isInPrivateKeeperMode() == True
  router.setInPrivateKeeperMode({"from":DEFAULT_ADMIN})
  assert router.isInPrivateKeeperMode() == False
  router.setInPrivateKeeperMode({"from":DEFAULT_ADMIN})
  assert router.isInPrivateKeeperMode() == True