from typing import Iterable

from .models import Invoice


async def get_invoice_by_id(invoice_id: int) -> Invoice:
    return await Invoice.get_or_none(id=invoice_id)


# if now address in usage -> return False
async def check_address_is_free(addr: str) -> bool:
    statuses = await Invoice.filter(recipient_addr=addr).values_list("active", flat=True)
    if True in statuses:
        return True
    return False


# async def get_all_active_invoices() -> Iterable[Invoice]:
#     x = await Invoice.filter(active=True)
#     return await Invoice.filter(active=True)


async def get_all_waiting_addresses() -> Iterable[str]:
    return await Invoice.filter(active=True).values_list("recipient_addr", flat=True)


async def test():
    invoices_id = [1]
    invoice = await Invoice.filter(id__in=invoices_id).all()