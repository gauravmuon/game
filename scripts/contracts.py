#!/usr/bin/python3
from brownie import accounts, Router, UpVsDownGameV2

# mind in accounts address 0 is owner and address 1 is game controller
def main():
    UpVsDownGameV2.deploy(accounts[1], "UpVsDownGameV2", {'from': accounts[0]})
    Router.deploy(accounts[1],accounts[0], {'from': accounts[0]})
