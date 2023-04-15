from pprint import pprint
from utils import validations
from fastapi import APIRouter
from database.models import Invoice, Invoice_Pydantic_Show, Invoice_Pydantic
from database import crud
# from utils.pydantict_to_dict import create_model_dict

router = APIRouter()


@router.get("/")
async def root():
    return {"status": "ok"}


@router.post("/new_invoice")
async def test(invoice: Invoice_Pydantic):
    validator = validations.Validator(invoice)
    try:
        validator.full_validation()
    except Exception as err:
        return {"status": "err", "desc": str(err)}
    is_active = await crud.check_address_is_free(invoice.recipient_addr)
    if is_active:
        return {"status": "err", "desc": "This address is already in use"}
    try:
        invoice_obj = await Invoice.create(**invoice.dict())
        return {"status": "ok", "desc": "Invoice has been created",
                "invoice": await Invoice_Pydantic_Show.from_tortoise_orm(invoice_obj)}
    except ValueError as err:
        return {"status": "err", "desc": f"{str(err)}"}


@router.get("/active_invoices", response_model=list[Invoice_Pydantic_Show])
async def get_transaction():
    return await Invoice_Pydantic_Show.from_queryset(Invoice.filter(active=True))


@router.get("/invoice/{invoice_id}")
async def get_invoice(invoice_id: int):
    invoice = await crud.get_invoice_by_id(invoice_id)
    if invoice:
        return await Invoice_Pydantic_Show.from_tortoise_orm(invoice)
    else:
        return {"status": "err", "desc": "invoice doesn't exist"}


@router.post("/invoices")
async def get_invoice(invoices_id: list[int]):
    queryset = Invoice.filter(id__in=invoices_id)
    return await Invoice_Pydantic_Show.from_queryset(queryset)


@router.delete("/invoice/{invoice_id}/")
async def get_invoice(invoice_id: int):
    invoice = await crud.get_invoice_by_id(invoice_id)
    invoice.active = False
    await invoice.save()
    if invoice:
        return {"status": "ok", "desc": "invoice deactivated"}
    else:
        return {"status": "err", "desc": "invoice doesn't exist"}