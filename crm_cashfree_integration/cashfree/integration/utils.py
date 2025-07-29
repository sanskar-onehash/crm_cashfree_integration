import frappe
import uuid
import pytz

from datetime import datetime


def get_base_uri():
    base_uri = str(frappe.db.get_single_value("Cashfree Integration", "base_uri") or "")
    if not base_uri.endswith("/"):
        base_uri += "/"
    return base_uri


def generate_unique_id():
    return uuid.uuid4()


def datetime_to_iso(dt: datetime | str):
    if isinstance(dt, str):
        frappe.utils.get_datetime(dt)
    tz = pytz.timezone(frappe.db.get_system_setting("time_zone") or "Asia/Kolkata")
    localized_dt = tz.localize(dt) if dt.tzinfo is None else dt.astimezone(tz)
    return localized_dt.isoformat()


def prepare_customer_details(customer_details: dict):
    customer_id = (customer_details["customer_id"] or "").strip()
    customer_phone = (customer_details["customer_phone"] or "").strip()

    if not customer_id or not customer_phone:
        frappe.throw("customer_id and customer_phone are mandatory")

    if " " in customer_id:
        customer_id = customer_id.replace(" ", "-")

    customer_details["customer_id"] = customer_id
    return customer_details
