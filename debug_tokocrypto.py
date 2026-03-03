import requests
import json

url = "https://www.tokocrypto.com/open/v1/market/klines"
params = {"symbol": "BTCUSDT", "interval": "1m", "limit": 5}
r = requests.get(url, params=params)
print(f"Status: {r.status_code}")
try:
    data = r.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Failed to parse JSON: {e}")
    print(r.text[:500])
