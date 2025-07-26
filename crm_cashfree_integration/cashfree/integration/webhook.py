import frappe
from crm_cashfree_integration.cashfree.integration import auth, service


@frappe.whitelist(allow_guest=True)
@auth.verify_webhook
def order_success():
    return service.handle_order_success()
