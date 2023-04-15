import asyncio
import json
from datetime import datetime, timedelta, timezone
from pprint import pprint
from typing import NamedTuple, Iterable
import aiohttp
from aiohttp import ContentTypeError
from database import crud
from database.models import Invoice
from loguru import logger
import settings


async def _get_all_transactions(address: str, min_timestamp: int) -> list:
    logger.debug("Send request to tron-grid")
    params = json.dumps({
        "only_to": True,
        "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "min_timestamp": min_timestamp
    })
    async with aiohttp.ClientSession() as client:
        async with client.get(f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20",
                              params=params) as resp:
            resp_j = await resp.json()
            return resp_j['data']


async def check_transaction_confirmation(transaction_id: str) -> bool:
    async with aiohttp.ClientSession() as client:
        url = f"https://api.trongrid.io/v1/transactions/{transaction_id}/events"
        async with client.get(url) as resp:
            resp_j = await resp.json()
            for tr in resp_j['data']:
                if tr["transaction_id"] == transaction_id:
                    if "_unconfirmed" in tr.keys():
                        return False
                    return True



satoshi = int


class TransactionStatus(NamedTuple):
    exist: bool
    confirmed: bool


def _find_transaction_by_amount(data: list, result: satoshi) -> str:
    # print(f'expect - {value}')
    for tx in data:
        dec = tx['token_info']['decimals']
        value = int(result * 10 ** dec)
        if int(tx['value']) == value:
            return tx["transaction_id"]


async def find_transaction(invoice: Invoice) -> str | bool:
    try:
        time_from = invoice.created_at.replace(tzinfo=timezone.utc).timestamp()
        timestamp = round(time_from*1000)
        data = await _get_all_transactions(invoice.recipient_addr, timestamp)

    except KeyError:
        invoice.active = False
        await invoice.save()
        return False

    except ContentTypeError:
        logger.error("Got blocked, start sleeping, need to switch proxy.")
        await asyncio.sleep(1000)
        return False

    if not data:
        logger.info("transaction is not found")
        return False
    transaction_id = _find_transaction_by_amount(data, invoice.expected_crypto_amount,)
    if not transaction_id:
        logger.info("transaction is not found")
        return False
    return transaction_id
    # await check_transaction_confirmation(transaction_id)


async def checking_trx_usdt_loop(sleep_sec=15):
    # while True:
    invoices = await crud.Invoice.filter(active=True, network="TRC20", coin="USDT")
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
            if invoice.transaction_id:
                confirmed = await check_transaction_confirmation(invoice.transaction_id)
            else:
                transaction_id = await find_transaction(invoice)
                if not transaction_id:
                    # await asyncio.sleep(sleep_sec)
                    continue
                logger.info(f"\ntransaction in invoice - {invoice.id} found")
                invoice.transaction_id = transaction_id
                invoice.transaction_found = True
                await invoice.save()
                confirmed = await check_transaction_confirmation(invoice.transaction_id)
            if confirmed:
                invoice.transaction_confirmed = True
                invoice.active = False
                await invoice.save()
                logger.info(f"\nInvoice - {invoice.id} confirmed\n"
                            f"{invoice.coin} {invoice.expected_crypto_amount} -> {round(invoice.expected_fiat_amount, 2)} {invoice.fiat}")


async def test():
    txs = await _get_all_transactions("bc1qg0yxkanrds2dla084hpu3huj07vcnq9naqqs3w")
    _find_transaction_by_amount(txs, 100, time_from=datetime.now())
