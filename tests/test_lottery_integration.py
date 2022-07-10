from brownie import network
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENT,
    fund_with_link,
    get_account,
    get_contract,
)
import pytest, time


def test_can_pick_winner():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery(
        # {"from": account, "gas_price": 100, "gas_limit": 12000000, "allow_revert": True}
        {"from": account, "gas_limit": 12000000, "allow_revert": True}
    )
    time.sleep(300)  # 5 mins wait for VRFCoordinator to responde
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
