#!/usr/bin/python3

import brownie
import random
import pytest

# mind in accounts address 0 is owner and address 1 is game controller

# initial call should give back true, for any pool id
def test_is_pool_open(upVsDownGameV2, accounts):
    is_pool_open = upVsDownGameV2.isPoolOpen(bytes(1))
    print(is_pool_open)
    assert is_pool_open

    random_num = int(random.random())
    is_pool_open = upVsDownGameV2.isPoolOpen(bytes(random_num))
    print(is_pool_open)
    assert is_pool_open
