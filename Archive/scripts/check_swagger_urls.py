"""Check what URLs are actually configured for Swagger"""
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Try to access the Swagger URLs directly
import requests

base_url = "http://127.0.0.1:8001"

endpoints = [
    "/swagger/",
    "/swagger",
    "/swagger.json",
    "/redoc/",
    "/api/swagger/",
]

print("Checking Swagger URLs...")
print("="*80)

for endpoint in endpoints:
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        print(f"[OK] {url:40} - Status: {response.status_code}")
        if response.status_code == 200 and 'swagger' in url:
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] {url:40} - Cannot connect")
    except Exception as e:
        print(f"[WARNING] {url:40} - Error: {e}")

print("\n" + "="*80)
print("\nTesting API endpoint:")
response = requests.get(f"{base_url}/api/v1/")
print(f"GET {base_url}/api/v1/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json() if response.status_code == 200 else response.text[:200]}")
