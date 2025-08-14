# Odos Router V3

## Deployments

The Odos router is deployed at `0x0D05a7D3448512B78fa8A9e46c4872C88C4a0D05` on all supported EVM chains.

## Overview

The Odos Router’s primary purpose is to serve as a security wrapper around the arbitrary execution of contract interactions to facilitate efficient token swaps. The Router holds user approvals and is in charge of ensuring that tokens are only transferred from the user in the specified amount when the user is executing a swap, and ensuring that the user then gets at least the specified minimum amount out. The router accommodates different variations of swaps, including both single to single and multi to multi swaps, as well as a few different approval mechanisms. The router also collects and holds revenue (via positive slippage and/or fees) from the swapping activity.

## Features

### Swapping

The primary functions of the router are the user-facing swap functions that facilitate token exchange for users. The router supports atomic multi-input and multi-output swaps via the internal `_swapMulti` function, but also supports slightly more gas efficient single to single swaps through the internal `_swap` function. Both functions collect positive slippage when it occurs (defined as the difference between the executed and quoted output when the executed output is higher).

Both `_swap` and `_swapMulti` have several externally facing functions that can be called. For accessing the user's ERC20s, both variants allow for traditional approvals made directly to the router, as well as the use of Uniswap's Permit2 contract (as seen here: https://github.com/Uniswap/permit2). Both variants also have a `compact` option, which uses a custom decoder written in Yul to allow for significantly less calldata to be necessary to describe the swap than the normal endpoints, as well as more efficient decoding. Although yul typically has low readability, security assumptions for these two functions are low since they make a call to the same internal function that is callable with arbitrary parameters via the normal endpoint. These compact variants can also make use of an immutable address list when `SLOAD` opcodes are cheaper than paying for the calldata needed to pass a full value in.

### Referrals

A referral code can be passed into the swap function as an argument when a swap is executed. If a referral fee is specified, it will be charged on the output(s) of the swap and send 80% of the fee to the specified fee recipient immediately, retaining the remaining 20% as router revenue similar to positive slippage. The referral info will then be emitted in the swap event in order to track the activity. If the referral fee recipient is specified as the address of the router contract, then there will be no split and the full fee will be retained inside of the contract.

### Owner Functionality

Through positive slippage and swap fees, the router collects and holds revenue. This revenue is held in the router in order to avoid extra gas fees during the user's swap for additional transfers. Therefore, all funds held in the router are considered revenue already owned by the `owner` role. To manage this revenue, the router has several `owner` protected functions. `writeAddressList` allows the owner to append new addresses (never change/remove) to the list for use in the compact decoders, for use when storage reads are cheaper than calldata costs.

The owner can also use the two remaining functions to access the collected revenue, `transferRouterFunds` and `swapRouterFunds`. `transferRouterFunds` allows for any ERC20 or ether held in the router to be transferred to a specified destination. `swapRouterFunds` meanwhile allows for funds held in the router to be directly used in a swap before being transferred - this is particularly useful for transferring out revenue in a single denomination (e.g. USDC) despite it originally being collected in many denominations. There is an additional `liquidator` role that can also access these functions, in order to allow for more flexibility in liquidating the revenue that is collected. `liquidator` can only be changed by the owner via `changeLiquidatorAddress`.

### Output Hooks

Optionally, a call to a hook can be triggered after a swap is done. This can be used to do things like initiating a bridge transaction, using the outputs to mint a liquidity position, or stake tokens inside a vote escrowed system.

## Setup

### Install foundry

```bash
curl -L https://foundry.paradigm.xyz | bash
```

### Install dependencies

```bash
forge install
```

This repo also uses poetry for python package management

```bash
poetry shell
poetry install
```

### Build contracts

```bash
forge build
```

### Deploy contracts

```bash
forge script script/RouterV3.s.sol --rpc-url <RPC_URL> ---broadcast -vvvv
```

Brownie relies on Ganache to simulate transactions. If not already installed, Ganache CLI can be installed with npm:

```bash
npm install -g ganache
```

## Running Tests

To test the Router's functionality, OdosWethExecutor.sol is provided as an example Odos Executor and OdosTransferHook as an example Odos Hook (Production Executors and Hooks will be much more complex but will interact with the router in the same way). The WETH and Permit2 contract directories are also provided as examples of what contracts the router may be interacting with. With the above dependencies installed, the full suite of tests can be run with

```bash
poetry run brownie test
```
