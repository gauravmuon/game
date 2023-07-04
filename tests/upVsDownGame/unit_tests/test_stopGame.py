#!/usr/bin/python3

import brownie
import pytest

# mind, in accounts address 0 is owner and address 1 is game controller

# initial address should be deployers address
def test_unauth_stop_game(upVsDownGameV2, accounts):
    try:
        game_stopped = upVsDownGameV2.stopGame(
            "No reason".encode(), {"from": accounts[1]})
        assert False
    except brownie.exceptions.VirtualMachineError:
        pass


def test_auth_stop_game(upVsDownGameV2, accounts):
    game_stopped = upVsDownGameV2.stopGame(
        bytes("No reason","utf-8"), {"from": accounts[0]})
    print(str(game_stopped.events))
    print(str(game_stopped.events["GameStopped"][0]["reason"],"utf-8"))
    assert game_stopped.events["GameStopped"]
    assert str(game_stopped.events["GameStopped"][0]["reason"],"utf-8") == "No reason"
