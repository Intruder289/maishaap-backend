"""
Check AZAMpay API Documentation for Correct Endpoint

This script fetches the Redoc documentation and attempts to find the correct checkout endpoint.
"""

import requests
import json
import re
from urllib.parse import urljoin

def fetch_redoc_spec(url):
    """Fetch OpenAPI/Swagger spec from Redoc"""
    try:
        # Redoc usually loads from a JSON/YAML spec
        # Try common spec paths
        spec_urls = [
            url.replace('/redoc', '/swagger.json'),
            url.replace('/redoc', '/openapi.json'),
            url.replace('/redoc', '/api-docs'),
            url.replace('/redoc', '/swagger.yaml'),
            url.replace('/redoc', '/openapi.yaml'),
            'https://sandbox.azampay.co.tz/swagger.json',
            'https://sandbox.azampay.co.tz/openapi.json',
        ]
        
        for spec_url in spec_urls:
            try:
                print(f"Trying: {spec_url}")
                response = requests.get(spec_url, timeout=10)
                if response.status_code == 200:
                    try:
                        return response.json()
                    except:
                        return response.text
            except:
                continue
        
        # Try to get the HTML and extract spec URL
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            html = response.text
            # Look for spec URL in the HTML
            spec_patterns = [
                r'spec-url["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'url["\']?\s*[:=]\s*["\']([^"\']*swagger[^"\']*)["\']',
                r'url["\']?\s*[:=]\s*["\']([^"\']*openapi[^"\']*)["\']',
            ]
            
            for pattern in spec_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    if match.startswith('http'):
                        spec_url = match
                    else:
                        spec_url = urljoin(url, match)
                    
                    try:
                        print(f"Found spec URL: {spec_url}")
                        spec_response = requests.get(spec_url, timeout=10)
                        if spec_response.status_code == 200:
                            try:
                                return spec_response.json()
                            except:
                                return spec_response.text
                    except:
                        continue
        
        return None
    except Exception as e:
        print(f"Error fetching spec: {e}")
        return None

def find_checkout_endpoints(spec):
    """Find checkout-related endpoints in the spec"""
    endpoints = []
    
    if isinstance(spec, dict):
        paths = spec.get('paths', {})
        for path, methods in paths.items():
            if any(keyword in path.lower() for keyword in ['checkout', 'mno', 'mobile', 'payment', 'transaction']):
                for method, details in methods.items():
                    if method.upper() in ['POST', 'PUT', 'PATCH']:
                        endpoints.append({
                            'path': path,
                            'method': method.upper(),
                            'summary': details.get('summary', ''),
                            'description': details.get('description', ''),
                            'tags': details.get('tags', [])
                        })
    elif isinstance(spec, str):
        # Try to parse as JSON
        try:
            spec = json.loads(spec)
            return find_checkout_endpoints(spec)
        except:
            # Search for endpoint patterns in text
            patterns = [
                r'["\'](/api/[^"\']*(?:checkout|mno|mobile|payment)[^"\']*)["\']',
                r'path["\']?\s*:\s*["\']([^"\']*(?:checkout|mno|mobile|payment)[^"\']*)["\']',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, spec, re.IGNORECASE)
                endpoints.extend([{'path': m, 'method': 'POST'} for m in matches])
    
    return endpoints

def main():
    print("="*80)
    print("AZAMpay API Documentation Checker")
    print("="*80)
    
    redoc_url = "https://developerdocs.azampay.co.tz/redoc"
    print(f"\nFetching documentation from: {redoc_url}")
    
    # Try to fetch the spec
    spec = fetch_redoc_spec(redoc_url)
    
    if spec:
        print("\n[OK] Successfully fetched API specification")
        
        # Save spec to file for inspection
        with open('azampay_spec.json', 'w', encoding='utf-8') as f:
            if isinstance(spec, dict):
                json.dump(spec, f, indent=2)
            else:
                f.write(spec)
        print("Saved spec to: azampay_spec.json")
        
        # Debug: Show spec structure
        if isinstance(spec, dict):
            print(f"\nSpec keys: {list(spec.keys())}")
            if 'paths' in spec:
                print(f"Number of paths: {len(spec['paths'])}")
                print(f"Sample paths: {list(spec['paths'].keys())[:5]}")
            if 'openapi' in spec:
                print(f"OpenAPI version: {spec.get('openapi')}")
            if 'swagger' in spec:
                print(f"Swagger version: {spec.get('swagger')}")
        
        print("\nSearching for checkout endpoints...")
        
        endpoints = find_checkout_endpoints(spec)
        
        if endpoints:
            print(f"\n[SUCCESS] Found {len(endpoints)} checkout-related endpoint(s):")
            print("="*80)
            for i, endpoint in enumerate(endpoints, 1):
                print(f"\n{i}. {endpoint['method']} {endpoint['path']}")
                if endpoint.get('summary'):
                    print(f"   Summary: {endpoint['summary']}")
                if endpoint.get('tags'):
                    print(f"   Tags: {', '.join(endpoint['tags'])}")
        else:
            print("\n[WARN] No checkout endpoints found in specification")
            print("\nExtracting all POST endpoints...")
            
            if isinstance(spec, dict):
                paths = spec.get('paths', {})
                post_endpoints = []
                for path, methods in paths.items():
                    if 'post' in methods:
                        post_endpoints.append({
                            'path': path,
                            'summary': methods['post'].get('summary', ''),
                            'description': methods['post'].get('description', ''),
                            'tags': methods['post'].get('tags', [])
                        })
                
                if post_endpoints:
                    print(f"\n[OK] Found {len(post_endpoints)} POST endpoint(s):")
                    print("="*80)
                    for i, ep in enumerate(post_endpoints, 1):
                        print(f"\n{i}. POST {ep['path']}")
                        if ep['summary']:
                            print(f"   Summary: {ep['summary']}")
                        if ep['tags']:
                            print(f"   Tags: {', '.join(ep['tags'])}")
                        if ep['description']:
                            desc = ep['description'][:200]
                            print(f"   Description: {desc}...")
                    
                    # Look for mobile money related
                    print("\n" + "="*80)
                    print("Mobile Money / MNO Related Endpoints:")
                    print("="*80)
                    mno_endpoints = [ep for ep in post_endpoints if any(
                        keyword in ep['path'].lower() or 
                        keyword in ep['summary'].lower() or
                        any(keyword in tag.lower() for tag in ep['tags'])
                        for keyword in ['mno', 'mobile', 'checkout', 'payment', 'transaction']
                    )]
                    
                    if mno_endpoints:
                        for i, ep in enumerate(mno_endpoints, 1):
                            print(f"\n{i}. POST {ep['path']}")
                            if ep['summary']:
                                print(f"   {ep['summary']}")
                    else:
                        print("\n[INFO] No mobile money endpoints found in filtered results")
                else:
                    print("\n[WARN] No POST endpoints found in specification")
                    
                # Also show all paths for reference
                print("\n" + "="*80)
                print("All Available Paths (for reference):")
                print("="*80)
                all_paths = list(paths.keys())
                for i, path in enumerate(all_paths[:30], 1):  # Show first 30
                    methods = [m.upper() for m in paths[path].keys() if m.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']]
                    print(f"  {i}. {', '.join(methods)} {path}")
                if len(all_paths) > 30:
                    print(f"  ... and {len(all_paths) - 30} more paths")
    else:
        print("\n[ERROR] Could not fetch API specification")
        print("\nManual Check Required:")
        print("="*80)
        print("1. Open https://developerdocs.azampay.co.tz/redoc in your browser")
        print("2. Look for endpoints related to:")
        print("   - 'checkout'")
        print("   - 'mobile money' or 'MNO'")
        print("   - 'payment' or 'transaction'")
        print("3. Find the exact path (e.g., /api/v1/...)")
        print("4. Note the HTTP method (should be POST)")
        print("5. Share the exact endpoint path with me")
    
    print("\n" + "="*80)
    print("Alternative: Check Swagger UI")
    print("="*80)
    print("Also try: https://sandbox.azampay.co.tz/swagger")
    print("This might have interactive API explorer")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
