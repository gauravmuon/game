#!/usr/bin/python3

import pytest

# mind, in accounts address 0 is owner and address 1 is game controller

# initial fee percentage should be 5
def test_initial_fee_percentage(upVsDownGameV2, accounts):
    assert upVsDownGameV2.feePercentage() == 5

# updating fee percentage in loop, even inclueds game controller id
@pytest.mark.parametrize("idx", range(0, 10))
def test_auth_update_fee_address(upVsDownGameV2, accounts, idx):
    upVsDownGameV2.changeGameFeePercentage(idx, {"from": accounts[0]})
    assert upVsDownGameV2.feePercentage() == idx


# check unauthorized access ie: test onlyOwner modifier
# such unauth access must crash the call
def test_unauth_update_fee_address(upVsDownGameV2, accounts):
    # first check using game controller address
    didCrash = False
    try:
        upVsDownGameV2.changeGameFeePercentage(10, {"from": accounts[1]})
    except:
        didCrash = True
    assert didCrash

    # then check with any random address
    didCrash = False
    try:
      upVsDownGameV2.changeGameFeePercentage(10, {"from": accounts[5]})
    except:
      didCrash = True
    assert didCrash
