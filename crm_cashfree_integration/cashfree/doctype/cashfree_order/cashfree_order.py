# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime
from crm_cashfree_integration.cashfree import utils
from crm_cashfree_integration.cashfree.integration import api, config
from datetime import datetime

ORDER_STATUS_MAP = {"ACTIVE": "Active", "PAID": "Paid", "EXPIRED": "Expired"}


class CashfreeOrder(Document):
    def before_submit(self):
        if not self.get("payment_entry"):
            frappe.throw("Payment Entry is required to submit CF Order")


@frappe.whitelist()
def create_order(
    order_currency="INR",
    order_amount=0,
    customer_details={},
    invoices=None,
    order_meta=None,
    order_expiry_time=None,
):
    customer_details = utils.ensure_dict(customer_details)
    invoices = utils.ensure_dict(invoices)
    order_meta = utils.ensure_dict(order_meta)

    if not customer_details:
        frappe.throw("customer_details is required")
    elif not customer_details.get("customer_id") or not customer_details.get(
        "customer_phone"
    ):
        frappe.throw("customer_id and customer_phone are mandatory in customer_details")

    customer_id = customer_details["customer_id"]
    order_meta = order_meta or {}
    invoices = invoices or []
    order_items = []

    if invoices:
        parsed = parse_invoices(invoices, order_currency, customer_id)
        order_amount = parsed["amount"]
        order_currency = parsed["currency"]
        invoices = parsed["invoices"]
        order_items = parsed["order_items"]
    elif not order_amount:
        frappe.throw("Either invoices or order_amount must be provided.")

    order_doc = create_cashfree_order(
        currency=order_currency,
        amount=order_amount,
        customer=customer_id,
        customer_details=customer_details,
        order_meta=order_meta,
        order_items=order_items,
        order_expiry_time=order_expiry_time,
        invoices=invoices,
    )

    return {
        "amount": order_doc.get("amount"),
        "currency": order_doc.get("currency"),
        "docname": order_doc.name,
        "payment_session_id": order_doc.get("payment_session_id"),
        "client_script_src": config.CLIENT_SCRIPT_SRC,
    }


def create_cashfree_order(
    currency: str,
    amount: float,
    customer: str,
    customer_details: dict,
    order_meta: dict = {},
    order_items: list = [],
    order_expiry_time: datetime | None = None,
    invoices: list[dict] = [],
):
    order = frappe.get_doc(
        {
            "doctype": "Cashfree Order",
            "currency": currency,
            "amount": amount,
            "customer": customer,
            "order_details": frappe.json.dumps(
                {
                    "customer_details": customer_details,
                    "order_items": order_items,
                    "order_meta": order_meta,
                }
            ),
            "expiry_time": order_expiry_time,
            "invoices": invoices,
        }
    ).insert()

    cf_response = api.create_cf_order(
        order_currency=currency,
        order_amount=amount,
        order_id=order.name,
        customer_details=customer_details,
        order_meta=order_meta,
        order_expiry_time=order_expiry_time,
    )

    order.db_set(
        {
            "order_id": cf_response["cf_order_id"],
            "payment_session_id": cf_response["payment_session_id"],
            "expiry_time": get_datetime(cf_response["order_expiry_time"]).replace(
                tzinfo=None
            ),
            "order_status": ORDER_STATUS_MAP.get(cf_response.get("order_status")),
        }
    )

    return order


def parse_invoices(
    invoices: list[dict],
    currency: str,
    customer_id: str | None = None,
):
    amount = 0
    order_items = []
    cf_invoices = []

    for invoice in invoices:
        invoice_type = invoice.get("invoice_type", "")
        invoice_id = invoice.get("invoice_id", "")
        invoice_doc = frappe.get_doc(invoice_type, invoice_id)
        invoice_customer = utils.get_or_throw(invoice_doc, "customer")
        invoice_currency = utils.get_or_throw(invoice_doc, "currency")
        invoice_amount = utils.get_or_throw(invoice_doc, "grand_total")

        amount += invoice_amount
        if not customer_id:
            customer_id = invoice_customer
        if not currency:
            currency = invoice_currency

        if customer_id != invoice_currency:
            frappe.throw("Customer doesn't matches across invoices.")
        elif currency != invoice_currency:
            frappe.throw("Currency doesn't matches across invoices.")

        for item in invoice_doc.get("items") or []:
            order_items.append(
                {
                    "item": item.get("item_name"),
                    "amount": item.get("base_amount"),
                    "currency": invoice_doc.get_company_default("default_currency"),
                }
            )
        cf_invoices.append({"invoice_type": invoice_type, "invoice": invoice_id})

    return {
        "currency": currency,
        "amount": amount,
        "customer": customer_id,
        "invoices": cf_invoices,
        "order_items": order_items,
    }
