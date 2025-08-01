import frappe
import requests

from crm_cashfree_integration.cashfree.integration import auth, utils
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry


def make_get_request(endpoint, params=None, raise_for_status=False):
    idempotency_key = utils.generate_unique_id().bytes
    res = requests.get(
        f"{utils.get_base_uri()}{endpoint}",
        params=params,
        headers=auth.get_headers(idempotency_key=idempotency_key),
    )
    if raise_for_status:
        res.raise_for_status()
    return res


def make_post_request(
    endpoint, data=None, json=None, params=None, raise_for_status=False
):
    idempotency_key = utils.generate_unique_id().bytes
    res = requests.post(
        f"{utils.get_base_uri()}{endpoint}",
        data=data,
        json=json,
        params=params,
        headers=auth.get_headers(idempotency_key=idempotency_key),
    )
    if raise_for_status:
        res.raise_for_status()
    return res


def handle_order_success(data, event_time, type):
    frappe.set_user("Administrator")
    order = data.get("order", {})
    payment = data.get("payment", {})

    order_doc = frappe.get_doc("Cashfree Order", order.get("order_id"))
    if order_doc.get("payment_status"):
        # Payment Entry is already created
        return

    order_doc.db_set({"mode_of_payment": "Cash", "payment_status": "Success"})
    pe = create_order_pe(order_doc).save()

    order_doc.update(
        {
            "payment_id": payment.get("cf_payment_id"),
            "international_payment": payment.get("international_payment").get(
                "international"
            ),
            "payment_entry": pe.name,
        }
    )
    order_doc = order_doc.save()
    if order_doc.get("reference_fieldname"):
        frappe.db.set_value(
            order_doc.get("reference_type"),
            order_doc.get("reference_doc"),
            order_doc.get("reference_fieldname"),
            pe.name,
        )
    return "success"


def handle_order_failed(data, event_time, type):
    frappe.set_user("Administrator")

    order = data.get("order", {})
    order_doc = frappe.get_doc("Cashfree Order", order.get("order_id"))

    payment_status = "Failed"
    if (data.get("payment") or {}).get("payment_status") == "USER_DROPPED":
        payment_status = "User Dropped"

    order_doc.update({"payment_status": payment_status})
    order_doc.save()


def create_order_pe(order_doc):
    pe = get_payment_entry(
        order_doc.doctype,
        order_doc.name,
        party_amount=order_doc.amount,
        party_type="Customer",
        payment_type="Receive",
        reference_date=frappe.utils.getdate(),
        ignore_permissions=True,
    )

    # get_payment_entry sets Cashfree Order as reference
    pe.update({"references": [], "docstatus": 1})
    for invoice in order_doc.get("invoices") or []:
        invoice_type = invoice.get("invoice_type")
        invoice_name = invoice.get("invoice")
        invoice_amount = frappe.db.get_value(invoice_type, invoice_name, "grand_total")
        pe.append(
            "references",
            {
                "reference_doctype": invoice_type,
                "reference_name": invoice_name,
                "allocated_amount": invoice_amount,
            },
        )

    return pe
