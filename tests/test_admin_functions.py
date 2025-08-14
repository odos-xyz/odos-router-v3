import brownie
import pytest
from test_lib import utils
from brownie import accounts


@pytest.fixture
def router():
    return brownie.OdosRouterV3.deploy(
        accounts[0].address,
        {
            "from": accounts[0],
        },
    )


@pytest.fixture
def weth_executor():
    WETH = brownie.WETH9.deploy(
        {
            "from": accounts[0],
        }
    )
    return brownie.OdosWETHExecutor.deploy(
        WETH.address,
        {
            "from": accounts[0],
        },
    )


def test_swap_protected(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    with brownie.reverts("Address not allowed"):
        router.swapRouterFunds(
            [
                [
                    "0x0000000000000000000000000000000000000000",
                    input_amount,
                    weth_executor.address,
                ]
            ],
            [[weth_address, input_amount, input_amount, accounts[1]]],
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            {
                "value": 0,
                "from": accounts[1],
            },
        )


def test_swap_slippage_exceeded(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    with brownie.reverts("Slippage Limit Exceeded"):
        router.swapRouterFunds(
            [
                [
                    "0x0000000000000000000000000000000000000000",
                    input_amount,
                    weth_executor.address,
                ]
            ],
            [[weth_address, input_amount + 1, input_amount + 1, accounts[1]]],
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            {
                "value": 0,
                "from": accounts[0],
            },
        )


def test_swap_router_funds(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[1])

    router.swapRouterFunds(
        [
            [
                "0x0000000000000000000000000000000000000000",
                input_amount,
                weth_executor.address,
            ]
        ],
        [[weth_address, input_amount, input_amount, accounts[1]]],
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        {
            "value": 0,
            "from": accounts[0],
        },
    )
    assert WETH.balanceOf(accounts[1]) - balance_before == input_amount

def test_liquidator_swap_router_funds(router, weth_executor):
    
    liquidator = utils.random_address()

    router.changeLiquidatorAddress(
        liquidator,
        {
            "from": accounts[0],
        },
    )
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[1])

    router.swapRouterFunds(
        [
            [
                "0x0000000000000000000000000000000000000000",
                input_amount,
                weth_executor.address,
            ]
        ],
        [[weth_address, input_amount, input_amount, accounts[1]]],
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        {
            "value": 0,
            "from": liquidator,
        },
    )
    assert WETH.balanceOf(accounts[1]) - balance_before == input_amount


def test_swap_router_funds_max(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[1])

    router.swapRouterFunds(
        [["0x0000000000000000000000000000000000000000", 0, weth_executor.address]],
        [[weth_address, input_amount, input_amount, accounts[1]]],
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        {
            "value": 0,
            "from": accounts[0],
        },
    )
    assert WETH.balanceOf(accounts[1]) - balance_before == input_amount


def test_write_address_list_protected(router, weth_executor):
    addresses_to_write = [utils.random_address() for i in range(3)]
    with brownie.reverts("OwnableUnauthorizedAccount: 0x33a4622b82d4c04a53e170c638b944ce27cffce3"):
        router.writeAddressList(
            addresses_to_write,
            {
                "from": accounts[1],
            },
        )


def test_write_address_list(router, weth_executor):

    addresses_to_write = [utils.random_address() for i in range(3)]
    router.writeAddressList(
        addresses_to_write,
        {
            "from": accounts[0],
        },
    )
    for i, address in enumerate(addresses_to_write):
        assert address == router.addressList(i)

def test_change_liquidator_protected(router, weth_executor):

    new_liquidator = utils.random_address()

    with brownie.reverts("OwnableUnauthorizedAccount: 0x33a4622b82d4c04a53e170c638b944ce27cffce3"):
        router.changeLiquidatorAddress(
            new_liquidator,
            {
                "from": accounts[1],
            },
        )


def test_change_liquidator(router, weth_executor):

    new_liquidator = utils.random_address()

    router.changeLiquidatorAddress(
        new_liquidator,
        {
            "from": accounts[0],
        },
    )
    assert new_liquidator == router.liquidatorAddress()


def test_transfer_funds_protected(router, weth_executor):
    with brownie.reverts("Address not allowed"):
        router.transferRouterFunds(
            [],
            [],
            accounts[0],
            {
                "from": accounts[1],
            },
        )


def test_transfer_funds(router, weth_executor):

    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    balance_before = accounts[1].balance()

    router.transferRouterFunds(
        ["0x0000000000000000000000000000000000000000"],
        [input_amount],
        accounts[1],
        {
            "from": accounts[0],
        },
    )
    assert accounts[1].balance() - balance_before == input_amount

def test_liquidator_transfer_funds(router, weth_executor):

    liquidator = utils.random_address()

    router.changeLiquidatorAddress(
        liquidator,
        {
            "from": accounts[0],
        },
    )
    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    balance_before = accounts[1].balance()

    router.transferRouterFunds(
        ["0x0000000000000000000000000000000000000000"],
        [input_amount],
        accounts[1],
        {
            "from": liquidator,
        },
    )
    assert accounts[1].balance() - balance_before == input_amount


def test_transfer_funds_max(router, weth_executor):

    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    balance_before = accounts[1].balance()

    router.transferRouterFunds(
        ["0x0000000000000000000000000000000000000000"],
        [0],
        accounts[1],
        {
            "from": accounts[0],
        },
    )
    assert accounts[1].balance() - balance_before == input_amount
