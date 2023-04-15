import asyncio
from datetime import datetime, timedelta, timezone
from typing import NamedTuple, Iterable
import aiohttp
from aiohttp import ContentTypeError
from database import crud
from database.models import Invoice
from loguru import logger
import settings


async def _get_all_btc_transactions(address: str):
    logger.debug("\nSend request - to blockchain.info (btc)")
    async with aiohttp.ClientSession() as client:
        async with client.get(f"https://blockchain.info/rawaddr/{address}") as resp:
            resp_j = await resp.json()
            return resp_j['txs']


satoshi = int


class TransactionStatus(NamedTuple):
    exist: bool
    confirmed: bool
    hash: str


def _find_transaction_by_amount(txs: list, result: satoshi, time_from: datetime) -> TransactionStatus:
    satoshi_amount = int(result * 10 ** 8)
    for tx in txs:
        time_from = time_from.replace(tzinfo=timezone.utc)
        transaction_time = datetime.fromtimestamp(tx['time']).replace(tzinfo=timezone.utc)
        if time_from > transaction_time:
            continue
        if tx['result'] == satoshi_amount:
            if tx['block_index'] and tx['block_height']:
                return TransactionStatus(exist=True, confirmed=True, hash=tx["hash"])
            return TransactionStatus(exist=True, confirmed=False, hash=tx["hash"])


async def check_invoice(invoice: Invoice):
    if invoice.transaction_confirmed:
        invoice.active = False
        await invoice.save()
        return
    try:
        txs = await _get_all_btc_transactions(invoice.recipient_addr)
    except KeyError:
        invoice.active = False
        await invoice.save()
        return False
    except ContentTypeError:
        logger.error("Got blocked, start sleeping, need to switch proxy.")
        await asyncio.sleep(1000)
        return
    updated_status = _find_transaction_by_amount(txs,
                                                 invoice.expected_crypto_amount,
                                                 invoice.created_at)
    if not updated_status:
        logger.info("transaction is not found")
        return
    if updated_status.exist and invoice.transaction_found == False:
        invoice.transaction_found = True
        invoice.transaction_id = updated_status.hash
        await invoice.save()
        logger.info(f"\ntransaction in invoice - {invoice.id} found")

    if updated_status.confirmed and invoice.transaction_confirmed == False:
        invoice.transaction_confirmed = True
        invoice.active = False
        invoice.transaction_id = updated_status.hash
        await invoice.save()
        logger.info(f"\nInvoice - {invoice.id} confirmed\n"
                    f"{invoice.coin} {invoice.expected_crypto_amount} -> {round(invoice.expected_fiat_amount, 2)} {invoice.fiat}")


async def checking_btc_loop(sleep_sec=20):
    invoices = await crud.Invoice.filter(active=True, network="BTC", coin="BTC")
    for invoice in invoices:
        created_at_aware = invoice.created_at.replace(tzinfo=timezone.utc)
        differ = datetime.now(timezone.utc) - created_at_aware
        differ_seconds = differ.total_seconds()
        if differ_seconds > settings.WAIT_UNTIL_FOUND and invoice.transaction_found == False:
            invoice.active = False
            logger.info(f"Invoice {invoice.id} - expired")
            await invoice.save()
        elif differ_seconds > settings.WAIT_CONFIRMATION and invoice.transaction_confirmed == False:
            invoice.active = False
            logger.info(f"Invoice {invoice.id} - expired, transaction unconfirmed!")
            await invoice.save()
        else:
            await check_invoice(invoice)
    await asyncio.sleep(sleep_sec)


# def check_btc_sync():
#     print('2')
#     # loop = asyncio.new_event_loop()
#     loop = asyncio.get_event_loop()
#     # loop.run_until_complete(checking_btc_loop())
#     loop.run_until_complete(checking_btc_loop())
#
#
# def check_btc():
#     import multiprocessing as ml
#     btc_proc = ml.Process(target=check_btc)
#     btc_proc.start()


async def test():
    txs = await _get_all_btc_transactions("bc1qg0yxkanrds2dla084hpu3huj07vcnq9naqqs3w")
    _find_transaction_by_amount(txs, 100, time_from=datetime.now())
