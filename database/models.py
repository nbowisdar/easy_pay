from utils import proj_enums as en
from decimal import Decimal

from pydantic import BaseModel, Extra
from tortoise import fields, models, Tortoise, run_async
from tortoise.contrib.pydantic import pydantic_model_creator

from utils.convert_crypto import convert_from_fiat


class Invoice(models.Model):
    id = fields.IntField(pk=True)
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    #: This is a username
    network = fields.CharField(max_length=20)
    fiat = fields.CharField(max_length=10)
    coin = fields.CharField(max_length=10)
    recipient_addr = fields.CharField(max_length=200)
    expected_fiat_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    expected_crypto_amount = fields.DecimalField(max_digits=20, decimal_places=8)
    transaction_found = fields.BooleanField(default=False)
    transaction_confirmed = fields.BooleanField(default=False)
    transaction_id = fields.CharField(max_length=200, null=True, default=None)

    async def save(self, *args, **kwargs):
        if not self.expected_crypto_amount:
            self.expected_crypto_amount = await convert_from_fiat(
                symbol=self.coin, fiat=self.fiat,
                amount=self.expected_fiat_amount,
            )
        return await super().save(*args, **kwargs)


class Invoice_Pydantic(BaseModel):
    network: str
    recipient_addr: str
    fiat: str
    coin: str
    expected_fiat_amount: int


Invoice_Pydantic_Show = pydantic_model_creator(Invoice)

# class Invoice_Pydantic_Show(Invoice_Pydantic_Show):
#     class Config:
#         extra = Extra.ignore

# class Invoices_Pydantic(BaseModel):

