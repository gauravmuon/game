#!/usr/bin/python3

import brownie
import pytest

# mind in accounts address 0 is owner and address 1 is game controller

# accessing private functions should crash 
def test_send_ether(upVsDownGameV2, accounts, ether):
    try:
        upVsDownGameV2.sendEther(accounts[5].address, 10*ether)
        assert False
    except AttributeError:
        pass
