# Unit Tests
# A way of testing the smallest pecies of code in an isolated instance.
from operator import indexOf
from brownie import Lottery, accounts, config, network, exceptions
from requests import request
from scripts.helpful_scripts import (
    fund_with_link,
    getAccount,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    getContract,
)
import pytest
from scripts.deploy import deploy_lottery
from web3 import Web3


def test_get_entrance_fees():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2,000 eth/usd
    # usdEntranceFee is 50
    # 2000/1 == 50/x == 0.025
    expected_entrance_fees = 250000000000
    entrance_fees = lottery.getEntranceFee()
    # Assert
    assert expected_entrance_fees == entrance_fees


def test_cant_enter_unless_starter():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": getAccount(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = getAccount()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = getAccount()
    lottery = deploy_lottery()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.LS() == 2


def test_for_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = getAccount()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": getAccount(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": getAccount(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    tx = lottery.endLottery({"from": account})
    requestId = tx.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    getContract("vrf_coordinator").callBackWithRandomness(
        requestId, STATIC_RNG, lottery.address, {"from": account}
    )
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    assert lottery.latestWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
