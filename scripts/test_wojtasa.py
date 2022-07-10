from brownie import Lottery, accounts


def ileToJe():
    lottery = Lottery.deploy(
        "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        {"from": accounts[0]},
    )
    print(f"{lottery.getEntranceFee()}")


def main():
    ileToJe()
