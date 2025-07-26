import frappe
import requests

from crm_cashfree_integration.cashfree.integration import auth, utils


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


def handle_order_success():
    try:
        order = frappe.form_dict.get("order", {})
        payment = frappe.form_dict.get("payment", {})

        order_doc = frappe.get_doc("Cashfree Order", order.get("order_id"))
        if order_doc.docstatus == 1:
            # Payment Entry is already created
            return

        pe = create_order_pe(order_doc).insert()

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
        order_doc.submit()
    except Exception as e:
        frappe.log_error("webhook", e)
    return "success"


def create_order_pe(order_doc):
    pe = frappe.get_doc(
        {
            "doctype": "Payment Entry",
            "party_type": "Customer",
            "party": order_doc.get("customer"),
            "paid_amount": order_doc.get("amount"),
        }
    )
    for invoice in order_doc.get("invoices") or []:
        pe.append(
            "references",
            {
                "reference_doctype": invoice.get("invoice_type"),
                "reference_name": invoice.get("invoice"),
            },
        )
    pe.validate()
    return pe
