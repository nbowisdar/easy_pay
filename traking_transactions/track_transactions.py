import asyncio
import multiprocessing as ml
from database import crud
from .track_btc import checking_btc_loop
from .track_trx_usdt import checking_trx_usdt_loop


async def start_checking():
    while True:
        # async with asyncio.TaskGroup() as tg:
        #     tg.create_task(checking_trx_usdt_loop())
        #     print(0)
        #     tg.create_task(checking_btc_loop())
        #     # check_btc()
        #     print('1')
        await checking_trx_usdt_loop()
        await checking_btc_loop(20)




    # trx_proc = ml.Process(target=check_btc)