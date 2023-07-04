#!/usr/bin/python3

import brownie
import pytest

# mind in accounts address 0 is owner and address 1 is game controller

# initial address should be deployers address
def test_initial_game_controller_address(upVsDownGameV2, accounts):
    assert upVsDownGameV2.gameController() == accounts[1].address

# updating fee addresses in loop, even inclueds game controller id
@pytest.mark.parametrize("idx", range(0,10)) 
def test_auth_update_game_controller_address(upVsDownGameV2, accounts, idx):
    # upVsDownGameV2.changeGameControllerAddress(game_controller account)
    upVsDownGameV2.changeGameControllerAddress(accounts[idx],{"from":accounts[0]})
    assert upVsDownGameV2.gameController() == accounts[idx].address


# check unauthorized access ie: test onlyGameController modifier
# such unauth access must crash the call
def test_unauth_update_game_controller_address(upVsDownGameV2, accounts):
    # first check using game controller address
    didCrash = False
    try:
        upVsDownGameV2.changeGameControllerAddress(accounts[1],{"from":accounts[1]})
    except:
        didCrash = True
    assert didCrash
        
    # then check with any random address
    didCrash = False
    try:
        upVsDownGameV2.changeGameControllerAddress(accounts[5],{"from":accounts[5]})
    except:
        didCrash = True
    assert didCrash


