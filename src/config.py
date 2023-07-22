import json
import os
import logging

from eth_account import Account
from web3.middleware.geth_poa import async_geth_poa_middleware
from web3 import AsyncWeb3

logging.basicConfig(level=logging.INFO)

# config
EXTERNAL_RPC = os.getenv("EXTERNAL_RPC")
SIBERIUM_RPC = os.getenv("SIBERIUM_RPC")

SIBERIUM_BRIDGE_ADDRESS = "0xcDE134ca3dA2a4bf50fe97a5512933A85D0B1Db3"
with open("abis/siberium_bridge.json") as f:
    SIBERIUM_BRIDGE_ABI = json.load(f)

EXTERNAL_BRIDGE_ADDRESS = "0x239eB04C217d63bf4B7cD42C4DeDC64254FD9475"
with open("abis/external_bridge.json") as f:
    EXTERNAL_BRIDGE_ABI = json.load(f)

BRIDGE_OWNER_PRIVATE_KEY = os.getenv("BRIDGE_OWNER_PRIVATE_KEY")

# fmt: off
TOKENS = [
    ("0x2E8D98fd126a32362F2Bd8aA427E59a1ec63F780", "0x3715B40a95DFC12B787194031d575A7790cE36f8"),  # USDT
    ("0x45AC379F019E48ca5dAC02E54F406F99F5088099", "0x7BB176B9E1a1614603968003CE7a6322D62c4632"),  # WBTC
    ("0xCCB14936C2E000ED8393A571D15A2672537838Ad", "0x671e75147afeCaC91c40754044316bAcA98b5b49"),  # WETH
]
# fmt: on

EXTERNAL_TO_SIBERIUM_TOKENS = {f: t for (f, t) in TOKENS}
SIBERIUM_TO_EXTERNAL_TOKENS = {t: f for (f, t) in TOKENS}


# globals
bridge_owner = Account.from_key(BRIDGE_OWNER_PRIVATE_KEY)
external_w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(EXTERNAL_RPC))
siberium_w3 = AsyncWeb3(
    AsyncWeb3.AsyncHTTPProvider(SIBERIUM_RPC), middlewares=[async_geth_poa_middleware]
)
external_bridge = external_w3.eth.contract(
    EXTERNAL_BRIDGE_ADDRESS, abi=EXTERNAL_BRIDGE_ABI
)
siberium_bridge = siberium_w3.eth.contract(
    SIBERIUM_BRIDGE_ADDRESS, abi=SIBERIUM_BRIDGE_ABI
)
