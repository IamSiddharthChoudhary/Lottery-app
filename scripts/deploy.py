from scripts.helpful_scripts import getAccount, getContract, fund_with_link
from brownie import Lottery, network, config, MockV3Aggregator
import time


def deploy_lottery():
    print("Deploying lottery...")
    account = getAccount()
    lottery = Lottery.deploy(
        getContract("eth_usd_price_feed").address,
        getContract("vrf_coordinator").address,
        getContract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False
        ),  # This means default value is false
    )
    print("Deployed lottery!!")
    return lottery


def starting_lottery():
    account = getAccount()
    lottery = Lottery[-1]
    startLottery = lottery.startLottery({"from": account})
    startLottery.wait(1)
    # to avoid errors
    print("The lottery has been started.")


def enter_lottery():
    account = getAccount()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    enterLottery = lottery.enter({"from": account, "value": value})
    enterLottery.wait(1)
    print("You entered the lottery.")


def end_lottery():
    account = getAccount()
    lottery = Lottery[-1]
    # Fund the contract and then end the lottery
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transactions = lottery.endLottery({"from": account})
    ending_transactions.wait(1)
    time.sleep(120)
    # waiting for callback
    # for giving time to request and recieve process to complete.
    print(f"{lottery.latestWinner()} is the winner")
    # but there will be no chainlink node to calculate the randomness for our ganache network


def main():
    deploy_lottery()
    starting_lottery()
    enter_lottery()
    end_lottery()
