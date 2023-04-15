import asyncio

from fastapi import FastAPI

from settings import DATABASE_CONFIG
from routers import users
from tortoise.contrib.fastapi import register_tortoise

from traking_transactions.track_transactions import start_checking

app = FastAPI()

app.include_router(users.router)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_checking())


register_tortoise(
    app, config=DATABASE_CONFIG
    # db_url="sqlite://db.sqlite3",
    # modules={"models": ["database.models"]},
    # generate_schemas=True,
    # add_exception_handlers=True,
)