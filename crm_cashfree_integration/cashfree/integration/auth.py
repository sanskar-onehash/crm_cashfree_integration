import frappe

from crm_cashfree_integration.cashfree.integration.config import API_VERSION


def get_headers(request_id=None, idempotency_key=None):
    cashfree_integration = frappe.get_single("Cashfree Integration")

    if not cashfree_integration.get("enabled"):
        frappe.throw("Cashfree Integration is disabled")

    return {
        "x-client-id": cashfree_integration.get("app_id"),
        "x-client-secret": cashfree_integration.get_password("secret_key"),
        "x-api-version": API_VERSION,
        "Content-Type": "application/json",
    }
