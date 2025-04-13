import pytest
import requests
import time
import os
import hashlib
import hmac
import urllib.parse
from dotenv import load_dotenv
import responses

# Load API keys from .env
load_dotenv()
APIKEY = os.environ["BINANCE_APIKEY_TEST"]
APISECRET = os.environ["BINANCE_APISECRET_TEST"]

base_url = "https://testnet.binance.vision"


def sign_params(params, secret):
    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(
        secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    params["signature"] = signature
    return params


# Old test: Place Market Order (actual functionality)
@pytest.mark.parametrize("quantity", [0.001, 0.01])
def test_place_market_order(quantity):
    url = f"{base_url}/api/v3/order"

    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": "0.001",
        "timestamp": int(time.time() * 1000)
    }

    signed_params = sign_params(params, APISECRET)
    response = requests.post(url, headers={"X-MBX-APIKEY": APIKEY}, params=signed_params)

    assert response.status_code == 200, f"Order placement failed! Status code: {response.status_code}"
    order_data = response.json()
    assert order_data["status"] == "FILLED", f"Order was not filled! Status: {order_data['status']}"


# Old test: Place and Fetch Order (place order and check the status)
def test_place_and_fetch_order():
    # Step 1: Place the order
    url = f"{base_url}/api/v3/order"
    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": "0.001",
        "price": "30000",
        "timestamp": int(time.time() * 1000)
    }

    signed_params = sign_params(params, APISECRET)
    place_response = requests.post(url, headers={"X-MBX-APIKEY": APIKEY}, params=signed_params)

    assert place_response.status_code == 200, f"Order placement failed! Status code: {place_response.status_code}"
    place_order_data = place_response.json()
    assert place_order_data["status"] == "NEW", f"Order not placed correctly! Status: {place_order_data['status']}"

    # Step 2: Fetch the order status
    order_id = place_order_data["orderId"]
    fetch_url = f"{base_url}/api/v3/order"
    fetch_params = {
        "symbol": "BTCUSDT",
        "orderId": order_id,
        "timestamp": int(time.time() * 1000)
    }
    signed_fetch_params = sign_params(fetch_params, APISECRET)

    fetch_response = requests.get(fetch_url, headers={"X-MBX-APIKEY": APIKEY}, params=signed_fetch_params)
    assert fetch_response.status_code == 200, f"Order fetch failed! Status code: {fetch_response.status_code}"
    fetch_order_data = fetch_response.json()
    assert fetch_order_data["status"] == "NEW", f"Order status fetch failed! Status: {fetch_order_data['status']}"


# New test: Mock response for placing a market order
@responses.activate
def test_place_market_order_mocked():
    url = f"{base_url}/api/v3/order"

    # Mock response for order placement (successful order)
    responses.add(
        responses.POST,
        url,
        json={
            "symbol": "BTCUSDT",
            "orderId": 2749370,
            "status": "FILLED",
            "side": "BUY",
            "type": "MARKET",
            "price": "60000.00000000",
            "origQty": "0.00100000",
            "executedQty": "0.00100000"
        },
        status=200
    )

    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": "0.001",
        "timestamp": int(time.time() * 1000)
    }

    signed_params = sign_params(params, APISECRET)
    response = requests.post(url, headers={"X-MBX-APIKEY": APIKEY}, params=signed_params)

    assert response.status_code == 200, f"Order placement failed! Status code: {response.status_code}"
    order_data = response.json()
    assert order_data["status"] == "FILLED", f"Order was not filled! Status: {order_data['status']}"


# New test: Mock rate limit error
@responses.activate
def test_rate_limit_error():
    url = f"{base_url}/api/v3/order"

    # Mock rate limit error response
    responses.add(
        responses.POST,
        url,
        json={
            "code": -1003,
            "msg": "Too many requests; please try again later."
        },
        status=429  # HTTP Status Code for Too Many Requests
    )

    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": "0.001",
        "timestamp": int(time.time() * 1000)
    }

    signed_params = sign_params(params, APISECRET)
    response = requests.post(url, headers={"X-MBX-APIKEY": APIKEY}, params=signed_params)

    assert response.status_code == 429, f"Expected 429 for rate limit, but got {response.status_code}"
    error_data = response.json()
    assert error_data["code"] == -1003, f"Unexpected error code: {error_data['code']}"
    assert error_data[
               "msg"] == "Too many requests; please try again later.", f"Unexpected error message: {error_data['msg']}"
