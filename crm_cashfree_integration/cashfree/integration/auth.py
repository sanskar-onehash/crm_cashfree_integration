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
        webhook_version = frappe.request.headers.get("x-webhook-version")
        if not webhook_version or webhook_version != INTEGRATION_VERSION:
            frappe.log_error("invalid_webhook_version", webhook_version)
            frappe.throw("Invalid x-webhook-version received.")

        cashfree_integration = frappe.get_single("Cashfree Integration")
        verifyCashfreesSignature(cashfree_integration.get_password("secret_key"))

        kwargs.pop("cmd")
        fn(*args, **kwargs)

    return wrapper


def verifyCashfreesSignature(secret_key):
    raw_body = frappe.request.data
    timestamp = frappe.request.headers["x-webhook-timestamp"]
    signature = frappe.request.headers["x-webhook-signature"]
    signature_data = timestamp + raw_body
    message = bytes(signature_data, "utf-8")
    secretkey = bytes(secret_key, "utf-8")
    generatedSignature = base64.b64encode(
        hmac.new(secretkey, message, digestmod=hashlib.sha256).digest()
    )
    computed_signature = str(generatedSignature, encoding="utf8")
    if computed_signature == signature:
        json_response = frappe.json.loads(raw_body)
        return json_response
    frappe.throw("Generated signature and received signature did not match.")
