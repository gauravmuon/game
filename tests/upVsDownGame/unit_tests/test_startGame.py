#!/usr/bin/python3

import brownie
import pytest

# mind, in accounts address 0 is owner and address 1 is game controller

def test_unauth_start_game(upVsDownGameV2, accounts):
    try:
        game_started = upVsDownGameV2.startGame({"from": accounts[1]})
        print(str(game_started))
        assert False
    except brownie.exceptions.VirtualMachineError:
        pass


def test_auth_start_game(upVsDownGameV2, accounts):
    game_started = upVsDownGameV2.startGame({"from": accounts[0]})
    print(type(game_started.events["GameStarted"]))
    # check if game started event emitted
    assert game_started.events["GameStarted"]
