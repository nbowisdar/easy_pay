DATABASE_CONFIG = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

SUPPORTED_COINS = ["BTC", "USDT", "BUSD"]

SUPPORTED_FAIT = ["UAH", "USD", "RUB"]

WAIT_UNTIL_FOUND = 1800000

WAIT_CONFIRMATION = 10000000

MINIUM_FIAT_DEPOSIT = 100
