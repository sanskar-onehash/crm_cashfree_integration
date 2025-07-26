import frappe


def get_or_throw(object, key):
    value = object.get(key)
    if not value:
        frappe.throw(f"{key} not found")
    return value
