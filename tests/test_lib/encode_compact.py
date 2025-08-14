import math
import random

from test_lib.utils import encode_address, encode_amount, encode_bytes, encode_bytes_string
from web3 import Web3


def construct_compact_swap_data(
    path_def_bytes,
    input_token,
    output_token,
    input_amount,
    output_quote,
    max_slippage_percent,
    executor,
    input_dest,
    output_dest,
    address_list,
    referral_code,
    referral_fee,
    referral_beneficiary
):
    compact_router_data = "0x"

    compact_router_data += encode_address(input_token, address_list)
    compact_router_data += encode_address(output_token, address_list)
    compact_router_data += encode_amount(input_amount)

    compact_router_data += encode_amount(output_quote)
    compact_router_data += encode_bytes_string(int(0xFFFFFF * max_slippage_percent), 3)
    compact_router_data += encode_address(executor, address_list)

    if input_dest == executor:
        compact_router_data += "0000"
    else:
        compact_router_data += encode_address(input_dest, address_list)

    if output_dest == "msg.sender":
        compact_router_data += "0000"
    else:
        compact_router_data += encode_address(output_dest, address_list)

    compact_router_data += encode_bytes_string(referral_code, 8)

    if referral_fee != 0:
        compact_router_data += "01"
        compact_router_data += encode_bytes_string(referral_fee, 8)
        compact_router_data += referral_beneficiary[2:].lower()
    else:
        compact_router_data += "00"

    compact_router_data += encode_bytes(path_def_bytes)

    return compact_router_data


def construct_compact_swap_multi_data(
    path_def_bytes,
    input_tokens,
    output_tokens,
    input_amounts,
    output_quotes,
    max_slippage_percent,
    executor,
    input_dests,
    output_dests,
    address_list,
    referral_code,
    referral_fee,
    referral_beneficiary
):
    compact_router_data = "0x"

    compact_router_data += encode_bytes_string(len(input_tokens), 1)
    compact_router_data += encode_bytes_string(len(output_tokens), 1)

    compact_router_data += encode_address(executor, address_list)
    compact_router_data += encode_bytes_string(int(0xFFFFFF * max_slippage_percent), 3)

    for i, input_token in enumerate(input_tokens):
        compact_router_data += encode_address(input_token, address_list)
        compact_router_data += encode_amount(input_amounts[i])

        if input_dests[i] == executor:
            compact_router_data += "0000"
        else:
            compact_router_data += encode_address(input_dests[i], address_list)

    for i, output_token in enumerate(output_tokens):
        compact_router_data += encode_address(output_token, address_list)
        compact_router_data += encode_amount(output_quotes[i])

        if output_dests[i] == "msg.sender":
            compact_router_data += "0000"
        else:
            compact_router_data += encode_address(output_dests[i], address_list)

    compact_router_data += encode_bytes_string(referral_code, 8)

    if referral_fee != 0:
        compact_router_data += "01"
        compact_router_data += encode_bytes_string(referral_fee, 8)
        compact_router_data += referral_beneficiary[2:].lower()
    else:
        compact_router_data += "00"

    compact_router_data += encode_bytes(path_def_bytes)

    return compact_router_data
