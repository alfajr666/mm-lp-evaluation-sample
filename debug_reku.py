import requests
import json

url = "https://api.reku.id/v2/orderbookall"
r = requests.get(url)
print(f"Status: {r.status_code}")
try:
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
except Exception as e:
    print(f"Failed to parse JSON: {e}")
    print(r.text[:500])

print("\nTrying with headers...")
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers)
print(f"Status: {r.status_code}")
try:
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
except Exception as e:
    print(f"Failed to parse JSON: {e}")
    print(r.text[:500])
