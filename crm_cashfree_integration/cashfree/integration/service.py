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
