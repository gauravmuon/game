#!/usr/bin/python3

import brownie
import time
import pytest

# mind, in accounts address 0 is owner and address 1 is game controller


# as game is not started, it should crash
def test_distrbute_game_not_started(upVsDownGameV2, accounts):
    try:
        upVsDownGameV2.distribute(
            bytes(1), 5, time.time(), {"from": accounts[1]})
        assert False
    except brownie.exceptions.VirtualMachineError:
        pass

# as pool dosen't exist it should crash
def test_distrbute_pool_not_exist(upVsDownGameV2, accounts):
    try:
        game_started = upVsDownGameV2.startGame({"from": accounts[0]})
        upVsDownGameV2.distribute(
            bytes(1), 5, time.time(), {"from": accounts[1]})
        assert False
    except brownie.exceptions.VirtualMachineError:
        pass

# as distribute is called by other than gamecontroller, it should crash
def test_distrbute_unauth_call(upVsDownGameV2, accounts, ether):
    try:
        game_started = upVsDownGameV2.startGame({"from": accounts[0]})
        pool_1 = upVsDownGameV2.createPool(
            bytes(1), 5*ether, 50*ether, 50*ether, {"from": accounts[1]})
        upVsDownGameV2.distribute(
            bytes(1), 5, time.time(), {"from": accounts[0]})
        assert False
    except brownie.exceptions.VirtualMachineError:
        pass


def test_distrbute_auth(upVsDownGameV2, accounts, ether):
    # starting the game by owner account
    game_started = upVsDownGameV2.startGame({"from": accounts[0]})
    # creating a pool by game controller account
    pool_1 = upVsDownGameV2.createPool(
        bytes(1), 5*ether, 50*ether, 50*ether, {"from": accounts[1]})

    distribute = upVsDownGameV2.distribute(
        bytes(1), 5, time.time(),  {"from": accounts[1]})
        
    print(str(distribute.events))
    assert distribute.events["RoundDistributed"][0]["totalWinners"] == 0
