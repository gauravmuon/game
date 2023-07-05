#!/usr/bin/python3

import helpers

def test_contract_registery(upVsDownGameV2, router, accounts, 
                    ether, ADMIN, DEFAULT_ADMIN):

  helpers.start_game_and_create_pool(upVsDownGameV2, ether, ADMIN, DEFAULT_ADMIN)

  assert router.contractRegistry(upVsDownGameV2.address) == False
  router.setContractRegistry(upVsDownGameV2.address, True, {"from":DEFAULT_ADMIN})
  assert router.contractRegistry(upVsDownGameV2.address) == True
  router.setContractRegistry(upVsDownGameV2.address, False, {"from":DEFAULT_ADMIN})
  assert router.contractRegistry(upVsDownGameV2.address) == False
  
  assert router.contractRegistry(accounts[5].address) == False
  router.setContractRegistry(accounts[5].address, False, {"from":DEFAULT_ADMIN})
  assert router.contractRegistry(accounts[5].address) == False
  router.setContractRegistry(accounts[5].address, True, {"from":DEFAULT_ADMIN})
  assert router.contractRegistry(accounts[5].address) == True
