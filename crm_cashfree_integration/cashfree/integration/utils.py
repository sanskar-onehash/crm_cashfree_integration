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


def datetime_to_iso(dt: datetime):
    tz = pytz.timezone(frappe.db.get_system_setting("time_zone") or "Asia/Kolkata")
    localized_dt = tz.localize(dt) if dt.tzinfo is None else dt.astimezone(tz)
    return localized_dt.isoformat()
