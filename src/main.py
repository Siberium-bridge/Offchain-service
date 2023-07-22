import asyncio
import logging

from config import (
    external_w3,
    siberium_w3,
    external_bridge,
    siberium_bridge,
    EXTERNAL_TO_SIBERIUM_TOKENS,
    SIBERIUM_TO_EXTERNAL_TOKENS,
    bridge_owner,
)

logger = logging.getLogger("bridge")


async def process_deposit(deposit_log):
    siberium_token = EXTERNAL_TO_SIBERIUM_TOKENS.get(deposit_log["args"]["token"])
    if siberium_token is None:
        return
    origin_tx = deposit_log["transactionHash"]

    if await siberium_bridge.functions.processedDeposits(origin_tx).call():
        return

    bridge_raw_tx = await siberium_bridge.functions.endDeposit(
        siberium_token,
        deposit_log["args"]["amount"],
        deposit_log["args"]["receiver"],
        origin_tx,
    ).build_transaction(
        {
            "from": bridge_owner.address,
            "nonce": await siberium_w3.eth.get_transaction_count(bridge_owner.address),
        }
    )
    tx_hash = await siberium_w3.eth.send_raw_transaction(
        siberium_w3.eth.account.sign_transaction(
            bridge_raw_tx, bridge_owner._private_key
        ).rawTransaction
    )
    logger.info(
        f"Deposit processed. External tx: {origin_tx.hex()}, Siberium tx: {tx_hash.hex()}"
    )


async def process_withdrawal(withdrawal_log):
    external_token = SIBERIUM_TO_EXTERNAL_TOKENS.get(withdrawal_log["args"]["token"])
    if external_token is None:
        return
    origin_tx = withdrawal_log["transactionHash"]

    if await external_bridge.functions.processedWithdrawals(origin_tx).call():
        return

    bridge_raw_tx = await external_bridge.functions.endWithdrawal(
        external_token,
        withdrawal_log["args"]["amount"],
        withdrawal_log["args"]["receiver"],
        origin_tx,
    ).build_transaction(
        {
            "from": bridge_owner.address,
            "nonce": await external_w3.eth.get_transaction_count(bridge_owner.address),
        }
    )
    tx_hash = await external_w3.eth.send_raw_transaction(
        external_w3.eth.account.sign_transaction(
            bridge_raw_tx, bridge_owner._private_key
        ).rawTransaction
    )
    logger.info(
        f"Withdrawal processed. Siberium tx: {origin_tx.hex()}, External tx: {tx_hash.hex()}"
    )


async def listen_deposits():
    logger.info("Listen for new deposits...")

    last_processed_external_block = await external_w3.eth.block_number
    while True:
        await asyncio.sleep(1)

        last_external_block = await external_w3.eth.block_number
        if last_external_block == last_processed_external_block:
            continue

        deposit_receipts = await external_bridge.events.DepositStarted().get_logs(
            {"fromBlock": last_processed_external_block, "toBlock": last_external_block}
        )
        last_processed_external_block = last_external_block
        for deposit_receipt in deposit_receipts:
            await process_deposit(deposit_receipt)


async def listen_withdrawals():
    logger.info("Listen for new withdrawals...")

    last_processed_siberium_block = await siberium_w3.eth.block_number
    while True:
        await asyncio.sleep(1)

        last_siberium_block = await siberium_w3.eth.block_number
        if last_siberium_block == last_processed_siberium_block:
            continue

        withdrawal_logs = await siberium_bridge.events.WithdrawalStarted().get_logs(
            {"fromBlock": last_processed_siberium_block, "toBlock": last_siberium_block}
        )
        last_processed_siberium_block = last_siberium_block
        for withdrawal_log in withdrawal_logs:
            await process_withdrawal(withdrawal_log)


async def main():
    await asyncio.gather(listen_deposits(), listen_withdrawals())


asyncio.run(main())
