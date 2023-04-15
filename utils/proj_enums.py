from enum import Enum


class Network(Enum):
    btc = "BTC"
    trx = "TRC20"
    bnb = "BEEP20"
    sol = "SOLANA"


class Coin(Enum):
    BTC = "BTC"
    TRX = "TRX"
    BNB = "BNB"
    SOL = "SOL"
    USDT = "USDT"


class Fiat(Enum):
    uah = "UAH"
    rub = "RUB"
    usd = "USD"