#!/usr/bin/python3

import brownie
import pytest

# mind in accounts address 0 is owner and address 1 is game controller

# private function should not exist
# accessing them must produce attribute error
def test_private_calculate_distribution(upVsDownGameV2, accounts):
    try:
        upVsDownGameV2.calculateDistribution()
        assert False
    except AttributeError:
        pass
