"""
Comprehensive AZAM Pay Integration Test Script

This script tests the complete AZAM Pay payment flow:
1. Login to get JWT token
2. Get bookings (no invoice required)
3. Create payment record for booking
4. Initiate gateway payment (AZAM Pay)
5. Verify payment status
6. View transactions

Usage:
    python test_azam_pay.py

Make sure:
    1. Django server is running (python manage.py runserver)
    2. You have valid AZAM Pay credentials in .env file
    3. You have at least one booking in the database
    4. User has a phone number in their profile
"""

import requests
import json
import sys
import time
import webbrowser
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8081"  # Updated to match your port
API_BASE = f"{BASE_URL}/api/v1"

# You'll need to get these after logging in
ACCESS_TOKEN = None
PAYMENT_ID = None
BOOKING_ID = None
TRANSACTION_ID = None
PAYMENT_LINK = None


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response, show_body=True):
    """Print HTTP response details"""
    print(f"\nStatus Code: {response.status_code}")
    if show_body:
        try:
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
        except:
            print("Response Text:")
            print(response.text)


def login(email=None, password=None):
    """Login and get access token"""
    print_section("Step 1: Login to Get JWT Token")
    
    if not email:
        print("\nEnter your login credentials:")
        email = input("Email: ").strip()
    
    if not password:
        import getpass
        password = getpass.getpass("Password: ").strip()
    
    url = f"{API_BASE}/auth/login/"
    data = {
        "email": email,  # Use email instead of username
        "password": password
    }
    
    print(f"\nPOST {url}")
    print(f"Email: {email}")
    print("Password: [HIDDEN]")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print_response(response)
        
        if response.status_code == 200:
            response_data = response.json()
            # Handle both response formats
            if 'tokens' in response_data:
                global ACCESS_TOKEN
                ACCESS_TOKEN = response_data['tokens'].get('access')
                print(f"\n[SUCCESS] Login successful!")
                print(f"Access Token: {ACCESS_TOKEN[:50]}...")
                if 'user' in response_data:
                    user = response_data['user']
                    print(f"User: {user.get('full_name', user.get('username', 'N/A'))}")
                return True
            elif 'access' in response_data:
                ACCESS_TOKEN = response_data.get('access')
                print(f"\n[SUCCESS] Login successful!")
                print(f"Access Token: {ACCESS_TOKEN[:50]}...")
                return True
            else:
                print("\n[ERROR] Unexpected response format!")
                return False
        else:
            print("\n[ERROR] Login failed!")
            if response.status_code == 400:
                try:
                    errors = response.json().get('errors', {})
                    print("Errors:", json.dumps(errors, indent=2))
                except:
                    pass
            return False
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to server at {BASE_URL}")
        print("Make sure Django server is running!")
        return False
    except Exception as e:
        print(f"\n[ERROR] Login error: {str(e)}")
        return False


def get_headers():
    """Get request headers with auth token"""
    if not ACCESS_TOKEN:
        return {}
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }


def get_bookings():
    """Get list of bookings"""
    print_section("Step 2: Get Bookings")
    
    url = f"{API_BASE}/bookings/"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if not results and isinstance(data, list):
                results = data
            
            if results:
                global BOOKING_ID
                # Use the first confirmed/pending booking, or first one available
                for booking in results:
                    if booking.get('status') in ['confirmed', 'pending']:
                        BOOKING_ID = booking.get('id')
                        print(f"\n[OK] Found {len(results)} booking(s)")
                        print(f"Using Booking ID: {BOOKING_ID}")
                        print(f"   Property: {booking.get('property_details', {}).get('name', 'N/A') if isinstance(booking.get('property_details'), dict) else 'N/A'}")
                        print(f"   Total Amount: TZS {booking.get('total_amount', 'N/A')}")
                        print(f"   Status: {booking.get('status', 'N/A')}")
                        return True
                
                # If no confirmed/pending booking, use first one
                BOOKING_ID = results[0].get('id')
                print(f"\n[OK] Found {len(results)} booking(s)")
                print(f"Using Booking ID: {BOOKING_ID}")
                print(f"   Property: {results[0].get('property_details', {}).get('name', 'N/A') if isinstance(results[0].get('property_details'), dict) else 'N/A'}")
                print(f"   Total Amount: TZS {results[0].get('total_amount', 'N/A')}")
                print(f"   Status: {results[0].get('status', 'N/A')}")
                return True
            else:
                print("\n[WARN] No bookings found!")
                print("Create a booking first:")
                print("   - Go to your admin panel")
                print("   - Create a booking for a property")
                print("   - Then run this script again")
                return False
        else:
            print(f"\n[ERROR] Failed to get bookings! (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"\n[ERROR] Error getting bookings: {str(e)}")
        return False


def create_payment():
    """Create a payment record for booking via web interface"""
    print_section("Step 3: Create Payment Record")
    
    if not BOOKING_ID:
        print("[ERROR] No booking ID available!")
        return False
    
    # Get booking details first
    try:
        booking_url = f"{API_BASE}/bookings/{BOOKING_ID}/"
        booking_resp = requests.get(booking_url, headers=get_headers(), timeout=10)
        if booking_resp.status_code == 200:
            booking_data = booking_resp.json()
            total_amount = booking_data.get('total_amount', '50000.00')
            print(f"\nUsing Booking ID: {BOOKING_ID}")
            print(f"   Booking Total: TZS {total_amount}")
        else:
            total_amount = "50000.00"
    except:
        total_amount = "50000.00"
    
    amount = input(f"Enter payment amount (or press Enter for TZS {total_amount}): ").strip()
    if not amount:
        amount = total_amount
    
    # Use the web payment creation endpoint which handles gateway initiation
    # This simulates what happens when you submit the payment form on the web
    payment_url = f"{BASE_URL}/properties/bookings/{BOOKING_ID}/payment/"
    
    # Create a session to maintain cookies
    session = requests.Session()
    session.headers.update(get_headers())
    
    # First, get the payment form page to get CSRF token if needed
    # Then POST the payment data
    form_data = {
        'amount': amount,
        'payment_method': 'online',  # Use 'online' for AZAM Pay
        'notes': f'Test payment for booking {BOOKING_ID}'
    }
    
    print(f"\nPOST {payment_url}")
    print(f"Data: {json.dumps(form_data, indent=2)}")
    print("\n[INFO] Note: This uses the web payment flow which creates payment and initiates gateway automatically")
    
    try:
        # Use the web endpoint - it will create payment and initiate gateway
        response = session.post(payment_url, data=form_data, timeout=30, allow_redirects=False)
        
        # Check if we got redirected (success) or got an error
        if response.status_code in [302, 301]:
            # Payment was initiated, redirected to payment link
            redirect_url = response.headers.get('Location', '')
            if 'azampay' in redirect_url.lower() or 'checkout' in redirect_url.lower():
                global PAYMENT_LINK
                PAYMENT_LINK = redirect_url
                print(f"\n[SUCCESS] Payment initiated successfully!")
                print(f"   Payment Link: {PAYMENT_LINK}")
                print(f"\n[INFO] Payment was created and gateway was initiated via web flow")
                return True
            else:
                print(f"\n[WARN] Got redirect but URL doesn't look like payment link: {redirect_url}")
                return True
        elif response.status_code == 200:
            # Check response content for success/error
            content = response.text
            if 'payment initiated' in content.lower() or 'azampay' in content.lower():
                print(f"\n[SUCCESS] Payment initiated (check response for payment link)")
                return True
            else:
                print(f"\n[WARN] Got 200 but unclear if payment was created. Check response.")
                print_response(response, show_body=False)
                return False
        else:
            print(f"\n[ERROR] Failed to create payment! (Status: {response.status_code})")
            print_response(response)
            return False
    except Exception as e:
        print(f"\n[ERROR] Error creating payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def initiate_gateway():
    """Initiate gateway payment"""
    print_section("Step 4: Initiate Gateway Payment (AZAM Pay)")
    
    if not PAYMENT_ID:
        print("[ERROR] No payment ID available!")
        return False
    
    # Try unified payments endpoint
    url = f"{API_BASE}/payments/payments/{PAYMENT_ID}/initiate/"
    print(f"POST {url}")
    print("\nCalling AZAM Pay API...")
    
    try:
        response = requests.post(url, headers=get_headers(), timeout=30)
        print_response(response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            global PAYMENT_LINK, TRANSACTION_ID
            
            PAYMENT_LINK = data.get('payment_link')
            TRANSACTION_ID = data.get('transaction_id')
            transaction_ref = data.get('transaction_reference') or data.get('reference')
            
            print(f"\n[SUCCESS] Payment initiated successfully!")
            print(f"Payment ID: {PAYMENT_ID}")
            if TRANSACTION_ID:
                print(f"Transaction ID: {TRANSACTION_ID}")
            if transaction_ref:
                print(f"Transaction Reference: {transaction_ref}")
            if PAYMENT_LINK:
                print(f"\nPayment Link:")
                print(f"   {PAYMENT_LINK}")
                print(f"\nNext Steps:")
                print(f"   1. The payment link will open in your browser")
                print(f"   2. Complete the payment on AZAM Pay sandbox")
                print(f"   3. After payment, we'll verify the status")
                
                # Ask if user wants to open the link
                open_link = input("\nOpen payment link in browser? (y/n): ").strip().lower()
                if open_link == 'y':
                    try:
                        webbrowser.open(PAYMENT_LINK)
                        print("[OK] Payment link opened in browser!")
                    except Exception as e:
                        print(f"[WARN] Could not open browser: {e}")
                        print(f"   Please manually open: {PAYMENT_LINK}")
            else:
                print("\n[WARN] No payment link returned!")
                print("Check the response above for details.")
            
            return True
        else:
            print("\n[ERROR] Failed to initiate gateway payment!")
            print("Check server logs for details.")
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print("Error details:", json.dumps(error_data, indent=2))
                except:
                    pass
            return False
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out! Check your internet connection and AZAM Pay sandbox availability.")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_payment():
    """Verify payment status"""
    print_section("Step 5: Verify Payment Status")
    
    if not PAYMENT_ID:
        print("[ERROR] No payment ID available!")
        return False
    
    url = f"{API_BASE}/payments/{PAYMENT_ID}/verify/"
    print(f"POST {url}")
    print("\nVerifying payment with AZAM Pay...")
    
    try:
        response = requests.post(url, headers=get_headers(), timeout=30)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            verified = data.get('verified')
            transaction_status = data.get('transaction_status')
            
            print(f"\n[SUCCESS] Payment verification complete!")
            print(f"Payment Status: {status}")
            print(f"Transaction Status: {transaction_status}")
            print(f"Verified: {verified}")
            
            if status == 'completed' and verified:
                print("\n[SUCCESS] Payment completed successfully!")
            elif status == 'pending':
                print("\n[INFO] Payment is still pending. Wait a moment and try again.")
            else:
                print(f"\n[WARN] Payment status: {status}")
            
            return True
        else:
            print("\n[ERROR] Failed to verify payment!")
            return False
    except Exception as e:
        print(f"\n[ERROR] Verification error: {str(e)}")
        return False


def get_transactions():
    """Get all transactions"""
    print_section("Step 6: View Payment Transactions")
    
    url = f"{API_BASE}/payments/transactions/"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            count = data.get('count', len(results))
            
            print(f"\n[OK] Found {count} transaction(s)")
            
            if results:
                print("\nRecent Transactions:")
                print("-" * 70)
                for i, txn in enumerate(results[:5], 1):  # Show first 5
                    print(f"\n{i}. Transaction #{txn.get('id')}")
                    print(f"   Payment ID: {txn.get('payment')}")
                    print(f"   Status: {txn.get('status', 'N/A')}")
                    print(f"   Provider: {txn.get('provider', {}).get('name', 'N/A') if isinstance(txn.get('provider'), dict) else 'N/A'}")
                    if txn.get('gateway_transaction_id'):
                        print(f"   Gateway ID: {txn.get('gateway_transaction_id')}")
                    if txn.get('azam_reference'):
                        print(f"   AZAM Ref: {txn.get('azam_reference')}")
                    print(f"   Created: {txn.get('created_at', 'N/A')}")
            
            return True
        else:
            print(f"\n[ERROR] Failed to get transactions! (Status: {response.status_code})")
            print_response(response, show_body=False)
            return False
    except Exception as e:
        print(f"\n[ERROR] Error getting transactions: {str(e)}")
        return False


def check_payment_status():
    """Check payment status without verification"""
    print_section("Check Payment Status")
    
    if not PAYMENT_ID:
        print("[ERROR] No payment ID available!")
        return False
    
    url = f"{API_BASE}/payments/{PAYMENT_ID}/"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            print("\nPayment Details:")
            print(f"   ID: {data.get('id')}")
            print(f"   Amount: TZS {data.get('amount', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Payment Method: {data.get('payment_method', 'N/A')}")
            if data.get('transaction_ref'):
                print(f"   Transaction Ref: {data.get('transaction_ref')}")
            return True
        else:
            print(f"\n[ERROR] Failed to get payment details (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        return False


def main():
    """Main test flow"""
    print("\n" + "=" * 70)
    print("  AZAM Pay Integration Test Script (Sandbox Mode)")
    print("=" * 70)
    print(f"\nTesting against: {BASE_URL}")
    print("Make sure:")
    print("   1. Django server is running")
    print("   2. AZAM Pay credentials are in .env file")
    print("   3. You have at least one booking")
    print("   4. User has a phone number in profile")
    
    # Get credentials
    print("\n" + "-" * 70)
    print("Authentication")
    print("-" * 70)
    
    # Run tests
    if not login():
        print("\n[ERROR] Cannot proceed without login. Exiting.")
        sys.exit(1)
    
    if not get_bookings():
        print("\n[WARN] Cannot proceed without bookings.")
        print("Create a booking first, then run this script again.")
        sys.exit(1)
    
    if not create_payment():
        print("\n[ERROR] Cannot proceed without payment. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("Payment Link Ready")
    print("=" * 70)
    
    # Gateway is already initiated in create_payment for web flow
    initiate_gateway()
    
    # Wait and verify
    print("\n" + "=" * 70)
    print("Waiting for payment completion...")
    print("=" * 70)
    
    if PAYMENT_LINK:
        print(f"\nComplete the payment on AZAM Pay sandbox")
        print(f"   Link: {PAYMENT_LINK}")
        
        # Wait a bit
        wait_time = input("\nHow many seconds to wait before verification? (default: 30): ").strip()
        try:
            wait_seconds = int(wait_time) if wait_time else 30
        except:
            wait_seconds = 30
        
        print(f"\nWaiting {wait_seconds} seconds...")
        for i in range(wait_seconds, 0, -5):
            print(f"   {i} seconds remaining...", end='\r')
            time.sleep(min(5, i))
        print("\n")
    
    # Check payment status first
    check_payment_status()
    
    # Verify payment
    print("\n" + "=" * 70)
    verify = input("Verify payment status with AZAM Pay? (y/n): ").strip().lower()
    if verify == 'y':
        verify_payment()
    
    # Show transactions
    print("\n" + "=" * 70)
    get_transactions()
    
    # Final summary
    print("\n" + "=" * 70)
    print("  [SUCCESS] Test Complete!")
    print("=" * 70)
    print("\nView Results:")
    print(f"   Phoenix Admin: {BASE_URL}/payments/transactions/")
    print(f"   API: {API_BASE}/payments/transactions/")
    print(f"   Payment Details: {API_BASE}/payments/{PAYMENT_ID}/")
    
    if PAYMENT_ID:
        print(f"\nPayment ID: {PAYMENT_ID}")
    if TRANSACTION_ID:
        print(f"Transaction ID: {TRANSACTION_ID}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
