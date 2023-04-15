import aiohttp
import asyncio
import decimal
import functools
import settings
from utils.proj_enums import Coin, Network, Fiat


def my_async_decorator(func):
    @functools.wraps(func)
    async def wrapper(active_transactions: list, *args, **kwargs):
        incr = decimal.Decimal('0.00000001')
        while True:
            result = await func(*args, **kwargs) + incr
            if result not in active_transactions:
                active_transactions.append(result)
                return result
            print(f"already in - {result}")
            incr = decimal.Decimal('0.00000001') + incr
    return wrapper


async def _get_price(symbol: str) -> float:
    params = {"symbol": symbol}
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.BINANCE_URL, params=params) as resp:
            data = await resp.json()
            if "price" in data.keys():
                return float(data['price'])
            raise Exception(f"Error, got unexpected response: {data}")


async def convert_to_fiat(symbol: str, amount: float, fiat: str) -> decimal.Decimal:
    price = await _get_price(symbol + fiat)
    amount_fiat = price * amount
    return decimal.Decimal(amount_fiat).quantize(decimal.Decimal('0.01'))


# @my_async_decorator
async def convert_from_fiat(*, symbol: str, amount: decimal.Decimal, fiat: str) -> decimal.Decimal:
    price = await _get_price(symbol + fiat)
    amount_crypto = amount / decimal.Decimal(str(price))
    return decimal.Decimal(amount_crypto).quantize(decimal.Decimal('0.00000001'))

# async def convert_to_uah(symbol: Coin, amount: float):

# async def test():
#     x = await convert_to_fiat(Coin.USDT, 10, Fiat.UAH)
#     b = await convert_to_fiat(Coin.USDT, 10, Fiat.RUB)
#     print(x)
#     print(b)
#
#     x = await convert_from_fiat(Coin.USDT, 40, Fiat.UAH)
#     b = await convert_from_fiat(Coin.USDT, 40, Fiat.RUB)
#     print(x)
#     print(b)

if __name__ == '__main__':
    asyncio.run(test())