from decimal import Decimal
from brownie import (
    config,
    accounts,
    network,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
)

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-cli"]

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]


def getAccount(index=None, id=None):

    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def getContract(contract_name):
    """If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the variable 'contract_to_mock'.
    You'll see examples like the 'link_token'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it
        Args:
            contract_name (string): This is the name that is referred to in the
            brownie config and 'contract_to_mock' variable.
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictionary. This could be either
            a mock or the 'real' contract on a live network.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deployMocks()
        contract = contract_type[-1]
        # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # Address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # Contract.from_abi allows us to get a contract from its abi and address.
        # MockV3Aggregator._name returns the name and MockV3AggregtorV3Interface.abi returns the abi
    return contract


DECIMALS = 8
INITIAL_VALUE = 2 * 10**8


def deployMocks(decimals=DECIMALS, initialValue=INITIAL_VALUE):
    print("Deploying Mocks...")
    account = getAccount()
    MockV3Aggregator.deploy(DECIMALS, INITIAL_VALUE, {"from": account})
    linkToken = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(linkToken.address, {"from": account})
    print("Deployed Mocks!!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else getAccount()
    link_token = link_token if link_token else getContract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # This can also be done with the help of interface
    tx.wait(1)
    print("Funded {}".format(contract_address))
    return tx


# def fund_with_link(
#     contract_address, account=None, link_token=None, amount=1000000000000000000
# ):
#     account = account if account else getAccount()
#     link_token = link_token if link_token else getContract("link_token")
#     ### Keep this line to show how it could be done without deploying a mock
#     # tx = interface.LinkTokenInterface(link_token.address).transfer(
#     #     contract_address, amount, {"from": account}
#     # )
#     tx = link_token.transfer(contract_address, amount, {"from": account})
#     print("Funded {}".format(contract_address))
#     return tx
