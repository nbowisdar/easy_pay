import re

import settings
from database.models import Invoice_Pydantic
import bech32



class Validator:
    def __init__(self, invoice: Invoice_Pydantic):
        self.invoice = invoice

    @staticmethod
    def is_valid_bitcoin_address(address: str) -> bool:
        pattern = "^(bc1|[13])[a-km-zA-HJ-NP-Z1-9]{25,34}$"
        pattern = re.compile(pattern)
        return pattern.match(address) is not None

    # @staticmethod
    # def is_valid_bech32_address(address: str):
    #     try:
    #         hrp, data = bech32.decode(address)
    #         return True if hrp == 'bc' or hrp == 'tb' else False
    #     except:
    #         raise ValueError("Wrong Bitcoin address")
    #
    # def _validate_address(self):
    #     if self.invoice.coin == "BTC" and self.invoice.network == "BTC":
    #         if not self.is_valid_bitcoin_address(self.invoice.recipient_addr):
    #             self.is_valid_bech32_address(self.invoice.recipient_addr)

    def _check_symbols_and_fiat(self):
        if self.invoice.coin not in settings.SUPPORTED_COINS:
            raise ValueError("Unsupported symbol!")
        elif self.invoice.fiat not in settings.SUPPORTED_FAIT:
            raise ValueError("Unsupported fiat!")

    def _check_correspondence(self):
        if self.invoice.coin == "BTC" and self.invoice.network != "BTC":
            raise Exception("Bitcoin lives only in BTC network")
        elif self.invoice.coin != "BTC" and self.invoice.network == "BTC":
            raise Exception("Bitcoin lives only in BTC network")

    def _check_minimum_fiat(self):
        if self.invoice.expected_fiat_amount < settings.MINIUM_FIAT_DEPOSIT:
            raise ValueError(f"Minimum deposit - {settings.MINIUM_FIAT_DEPOSIT}")

    def full_validation(self):
        # self._validate_address()
        self._check_symbols_and_fiat()
        self._check_correspondence()
        self._check_minimum_fiat()


def test():
    addr = "bc1pw96py6dcp00js8ffac7rwsrzjqtj2hkk39ulk0quhmja72yss50sdqcjvd"
    assert Validator.is_valid_bech32_address(addr)


if __name__ == '__main__':
    test()