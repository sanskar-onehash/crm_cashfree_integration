import frappe
import base64
import hashlib
import hmac
from crm_cashfree_integration.cashfree.integration.config import INTEGRATION_VERSION


def get_headers(request_id=None, idempotency_key=None):
    cashfree_integration = frappe.get_single("Cashfree Integration")

    if not cashfree_integration.get("enabled"):
        frappe.throw("Cashfree Integration is disabled")

    return {
        "x-client-id": cashfree_integration.get("app_id"),
        "x-client-secret": cashfree_integration.get_password("secret_key"),
        "x-api-version": INTEGRATION_VERSION,
        "Content-Type": "application/json",
    }


def verify_webhook(fn):
    def wrapper(*args, **kwargs):
        webhook_version = frappe.request.headers["X-Webhook-Version"]
        if not webhook_version or webhook_version != INTEGRATION_VERSION:
            frappe.throw("Invalid X-Webhook-Version received.")

        cashfree_enabled = frappe.db.get_single_value("Cashfree Integration", "enabled")
        if not cashfree_enabled:
            # We can safely return
            return "success"

        cashfree_secret_key = frappe.db.get_single_value(
            "Cashfree Integration", "secret_key"
        )
        verifyCashfreeSignature(cashfree_secret_key)

        kwargs.pop("cmd")
        fn(*args, **kwargs)

    return wrapper


def verifyCashfreeSignature(secret_key):
    raw_body = frappe.request.data.decode("utf-8")
    timestamp = frappe.request.headers["X-Webhook-Timestamp"]
    signature = frappe.request.headers["X-Webhook-Signature"]
    signature_data = timestamp + raw_body
    message = bytes(signature_data, "utf-8")
    secretkey = bytes(secret_key, "utf-8")
    generatedSignature = base64.b64encode(
        hmac.new(secretkey, message, digestmod=hashlib.sha256).digest()
    )
    computed_signature = str(generatedSignature, encoding="utf8")
    if computed_signature != signature:
        frappe.throw("Generated signature and received signature did not match.")
