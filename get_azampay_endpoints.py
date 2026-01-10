"""
Get AZAMpay endpoints from the actual API spec
"""

import requests
import json

def main():
    print("Fetching AZAMpay Sandbox API specification...")
    
    spec_url = "https://developerdocs.azampay.co.tz/swagger/json/azampay.sandbox.json"
    
    try:
        response = requests.get(spec_url, timeout=30)
        response.raise_for_status()
        
        spec = response.json()
        
        # Save full spec
        with open('azampay_sandbox_spec.json', 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)
        print(f"[OK] Saved full spec to azampay_sandbox_spec.json")
        
        # Extract paths
        paths = spec.get('paths', {})
        print(f"\n[OK] Found {len(paths)} endpoint paths")
        
        # Find checkout/mno/mobile money related
        print("\n" + "="*80)
        print("CHECKOUT / MNO / MOBILE MONEY ENDPOINTS:")
        print("="*80)
        
        relevant_paths = []
        for path, methods in paths.items():
            path_lower = path.lower()
            for method, details in methods.items():
                if method.upper() == 'POST':
                    summary = details.get('summary', '').lower()
                    description = details.get('description', '').lower()
                    tags = [t.lower() for t in details.get('tags', [])]
                    
                    if any(keyword in path_lower or keyword in summary or keyword in description or any(keyword in tag for tag in tags)
                           for keyword in ['checkout', 'mno', 'mobile', 'payment', 'transaction', 'mpesa', 'tigo', 'airtel']):
                        relevant_paths.append({
                            'path': path,
                            'method': method.upper(),
                            'summary': details.get('summary', ''),
                            'tags': details.get('tags', [])
                        })
        
        if relevant_paths:
            for i, ep in enumerate(relevant_paths, 1):
                print(f"\n{i}. {ep['method']} {ep['path']}")
                if ep['summary']:
                    print(f"   Summary: {ep['summary']}")
                if ep['tags']:
                    print(f"   Tags: {', '.join(ep['tags'])}")
        else:
            print("\n[WARN] No checkout/MNO endpoints found with keywords")
            print("\nShowing all POST endpoints:")
            print("="*80)
            post_endpoints = []
            for path, methods in paths.items():
                if 'post' in methods:
                    post_endpoints.append({
                        'path': path,
                        'summary': methods['post'].get('summary', ''),
                        'tags': methods['post'].get('tags', [])
                    })
            
            for i, ep in enumerate(post_endpoints, 1):
                print(f"\n{i}. POST {ep['path']}")
                if ep['summary']:
                    print(f"   {ep['summary']}")
                if ep['tags']:
                    print(f"   Tags: {', '.join(ep['tags'])}")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
