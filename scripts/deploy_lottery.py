from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    startLottery_tx = lottery.startLottery({"from": account})
    startLottery_tx.wait(1)
    print("Lottery is started!")


def enter_lotery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract with link tokens for randomness function
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    end_lottery_tx = lottery.endLottery({"from": account})
    end_lottery_tx.wait(1)
    time.sleep(
        120
    )  # during endLottery we are waiting for a callback from requestRandmomness, lets give it a minute
    print(f"{lottery.recentWinner()} is the winner!!!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lotery()
    # end_lottery()
