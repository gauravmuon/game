#!/usr/bin/python3

import helpers 

def test_register_deregister(upVsDownGameV2, router, accounts, 
                    ether, ADMIN, DEFAULT_ADMIN):

  helpers.start_game_and_create_pool(upVsDownGameV2, ether, ADMIN, DEFAULT_ADMIN)

  # =================== registeration ================
  router.registerAccount(accounts[4].address, {"from":accounts[3]})
  # accountMapping(address) -> (address, nounce)
  assert router.accountMapping(accounts[3].address)[1] == 0 #nounce
  assert router.accountMapping(accounts[3].address)[0] == accounts[4].address

  router.registerAccount(accounts[5].address, {"from":accounts[3]})
  assert router.accountMapping(accounts[3].address)[1] == 0 #nounce
  assert router.accountMapping(accounts[3].address)[0] == accounts[5].address

  router.registerAccount(accounts[5].address, {"from":accounts[3]})
  assert router.accountMapping(accounts[3].address)[1] == 0 #nounce
  assert router.accountMapping(accounts[3].address)[0] == accounts[5].address

  router.registerAccount(accounts[8].address, {"from":accounts[7]})
  assert router.accountMapping(accounts[7].address)[0] == accounts[8].address

  router.registerAccount(accounts[9].address, {"from":accounts[8]})
  assert router.accountMapping(accounts[8].address)[0] == accounts[9].address

  # =================== deregisteration ================
  # deregistering the never registerd account increases nounce
  router.deregisterAccount({"from":accounts[2]})
  assert router.accountMapping(accounts[2].address)[1] == 1 #nounce
  assert router.accountMapping(accounts[2].address)[0] == "0x0000000000000000000000000000000000000000"

  # deregistering the registerd account increases nounce and set address to 0
  router.deregisterAccount({"from":accounts[3]})
  assert router.accountMapping(accounts[3].address)[1] == 1 #nounce
  assert router.accountMapping(accounts[3].address)[0] == "0x0000000000000000000000000000000000000000"

  router.deregisterAccount({"from":accounts[3]})
  assert router.accountMapping(accounts[3].address)[1] == 2 #nounce
  assert router.accountMapping(accounts[3].address)[0] == "0x0000000000000000000000000000000000000000"

  # =================== registeration ================
  # registeration never tweaks nounce value
  router.registerAccount(accounts[5].address, {"from":accounts[3]})
  assert router.accountMapping(accounts[3].address)[1] == 2 #nounce
  assert router.accountMapping(accounts[3].address)[0] == accounts[5].address
