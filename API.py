import asyncio
from pprint import pprint

import aiohttp
from pydantic import BaseModel
from decimal import Decimal


class Invoice_Pydantic(BaseModel):
    network: str
    recipient_addr: str
    fiat: str
    coin: str
    expected_fiat_amount: int


BASE_URL = "http://127.0.0.1:8000/"


async def check_server() -> dict:
    async with aiohttp.ClientSession() as client:
        headers = {'Content-Type': 'application/json'}
        async with client.get(BASE_URL, headers=headers) as resp:
            return await resp.json()


async def create_invoice(invoice: Invoice_Pydantic) -> dict:
    async with aiohttp.ClientSession() as client:
        headers = {'Content-Type': 'application/json'}

        async with client.post(BASE_URL + "new_invoice", headers=headers,
                              json=invoice.dict()) as resp:
            return await resp.json()


async def check_invoices(invoices_id: list[int]) -> dict:
    async with aiohttp.ClientSession() as client:
        # body = {}
        headers = {'Content-Type': 'application/json'}
        async with client.post(BASE_URL + "invoices",
                               headers=headers, json=invoices_id) as resp:
            return await resp.json()


async def deactivate_invoice(invoice_id: int | str) -> dict:
    async with aiohttp.ClientSession() as client:
        headers = {'Content-Type': 'application/json'}
        async with client.delete(f"{BASE_URL}invoice/{invoice_id}",
                                 headers=headers) as resp:
            return await resp.json()


async def test():
    # await check_invoices([3,4,5])
    # x = await check_server()
    # resp = await deactivate_invoice(3)
    # pprint(resp)
    inv = Invoice_Pydantic(network="BTC", coin="BTC", fiat="UAH", recipient_addr="addr1",
                          expected_fiat_amount=500)

    resp = await create_invoice(inv)
    pprint(resp)

asyncio.run(test())