#!/usr/bin/python3

import brownie
import pytest

# mind, in accounts address 0 is owner and address 1 is game controller

# initial pending distribution should be false
def test_has_pending_distributions(upVsDownGameV2, accounts):
    distribution = upVsDownGameV2.hasPendingDistributions(bytes(1))
    assert distribution == False
