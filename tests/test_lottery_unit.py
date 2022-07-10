from brownie import Lottery, accounts, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENT,
    fund_with_link,
    get_account,
    get_contract,
)
from web3 import Web3
import pytest

# this UT is to verify correct entrance fee value
def test_get_entrance_fee():
    # Arrange
    # this is unit test, we only execute it in local environment
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    lottery = deploy_lottery()

    # Act
    # eth price is 2000 from mock
    # usd entry fee is $50 so entrance fee = 50 / 2000 == 0.025eth
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()

    # Assert
    assert expected_entrance_fee == entrance_fee


# this test is to verify that one cant enter lottery until it is started
def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    lottery = deploy_lottery()

    # Act / Assert
    with pytest.raises(
        exceptions.VirtualMachineError
    ):  # we are expecting this to be failed
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    fund_with_link(lottery)

    # Act
    lottery.endLottery({"from": account})

    # Assert
    assert lottery.lottery_state() == 3  # 3 == CALCULATING_WINNER


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})

    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)

    starting_account_balance = account.balance()
    # print(f"Account balance before lottery ends is: {starting_account_balance}")
    balance_of_lottery = lottery.balance()
    # print(f"Lottery balance before lottery ends is: {balance_of_lottery}")

    tx = lottery.endLottery({"from": account})
    request_id = tx.events["RequestedRandomness"]["requestID"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )

    # Assert
    # 777 % 3 = 0
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_account_balance + balance_of_lottery
