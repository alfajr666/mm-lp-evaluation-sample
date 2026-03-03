import requests
import json

def test_url(url, params=None, name=""):
    print(f"--- Testing {name} ---")
    print(f"URL: {url}")
    print(f"Params: {params}")
    try:
        r = requests.get(url, params=params, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Tokocrypto variations
test_url("https://www.tokocrypto.com/open/v1/market/klines", {"symbol": "BTC_USDT", "interval": "1m", "limit": 1}, "Tokocrypto BTC_USDT")
test_url("https://www.tokocrypto.com/open/v1/market/klines", {"symbol": "btcusdt", "interval": "1m", "limit": 1}, "Tokocrypto btcusdt")
test_url("https://api.tokocrypto.com/api/v3/klines", {"symbol": "BTCUSDT", "interval": "1m", "limit": 1}, "Tokocrypto api.tokocrypto.com BTCUSDT")

# Reku variations
test_url("https://api.reku.id/v2/orderbookall", None, "Reku orderbookall")
test_url("https://api.reku.id/v2/orderbook", {"symbol": "btcidr"}, "Reku orderbook btcidr")
test_url("https://api.reku.id/v2/orderbook", {"symbol": "BTCIDR"}, "Reku orderbook BTCIDR")
test_url("https://api.reku.id/v1/orderbook/BTCIDR", None, "Reku v1 orderbook BTCIDR")
