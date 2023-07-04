#!/usr/bin/python3

import brownie
import pytest

# mind in accounts address 0 is owner and address 1 is game controller

# private function should not exist
# accessing them must produce attribute error
def test_auth_create_pool(upVsDownGameV2, accounts):
    upVsDownGameV2.createPool(bytes(1), 10, 100, 50, {"from":accounts[1]})
    pool = upVsDownGameV2.pools(bytes(1))
    assert pool[0] == True

# for unauth access it should crash, using owner id
def test_unauth_create_pool(upVsDownGameV2, accounts):
    didCrash = False
    try:
        upVsDownGameV2.createPool(bytes(1), 10, 100, 50, {"from":accounts[0]})
    except:
        didCrash = True
    assert didCrash

@pytest.mark.parametrize("idx", range(2,5)) 
def test_unauth_inloop_create_pool(upVsDownGameV2, accounts, idx):
    didCrash = False
    try:
        upVsDownGameV2.createPool(bytes(1), 10, 100, 50, {"from":accounts[idx]})
    except:
        didCrash = True
    assert didCrash

@pytest.mark.parametrize("idx", range(5)) 
def test_change_game_controller_then_create_pool(upVsDownGameV2, accounts, idx):
    # only owner can change game controller, updating new id as game controller 
    upVsDownGameV2.changeGameControllerAddress(accounts[idx],{"from":accounts[0]})
    # using new game contorller to update create a pool
    upVsDownGameV2.createPool(bytes(idx), 10, 100, 50, {"from":accounts[idx]})
    pool = upVsDownGameV2.pools(bytes(idx))
    assert pool[0] == True
