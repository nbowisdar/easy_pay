# from database.models import Invoice_Pydantic, Invoice_Pydantic_Show, Invoice
# # from proj_enums import Coin, Network, Fiat
#
#
# def create_model_dict(invoice: Invoice) -> Invoice_Pydantic_Show:
#     invoice_dict = invoice.__dict__  # convert the instance to a dictionary
#     invoice_dict["network"] = invoice_dict["network"].value  # convert the enum to a string
#     invoice_dict["fiat"] = invoice_dict["fiat"].value  # convert the enum to a string
#     invoice_dict["coin"] = invoice_dict["coin"].value  # convert the enum to a string
#     return Invoice_Pydantic_Show(**invoice_dict)  # create the Pydantic model instance
