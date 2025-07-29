from crm_cashfree_integration.cashfree.integration import service, utils
from datetime import datetime


def create_cf_order(
    order_currency: str,
    order_amount: float,
    order_id: str,
    customer_details: dict,
    order_expiry_time: str | datetime | None = None,
    order_meta: dict | None = None,
):
    if order_expiry_time:
        order_expiry_time = utils.datetime_to_iso(order_expiry_time)

    res = service.make_post_request(
        "orders",
        json={
            "order_amount": order_amount,
            "order_currency": order_currency,
            "order_id": order_id,
            "customer_details": utils.prepare_customer_details(customer_details),
            "order_expiry_time": order_expiry_time,
            "order_meta": order_meta,
        },
        raise_for_status=True,
    )
    return res.json()
