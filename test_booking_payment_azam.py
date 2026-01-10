"""
Comprehensive Test Script: Property Booking Payment via AZAM Pay

This script tests the complete flow:
1. Login to get JWT token
2. Get available properties (hotel, house, lodge, etc.)
3. Create a booking for a property
4. Create a payment for the booking
5. Initiate AZAM Pay payment
6. Verify payment status
7. View transaction details

Usage:
    python test_booking_payment_azam.py

Make sure:
    1. Django server is running
    2. AZAM Pay credentials are in .env file
    3. You have properties in the database
    4. User has a phone number in profile
"""

import requests
import json
import sys
import time
import webbrowser
from datetime import datetime, timedelta
from getpass import getpass

# Configuration
BASE_URL = "http://localhost:8081"
API_BASE = f"{BASE_URL}/api/v1"

# Global variables
ACCESS_TOKEN = None
PROPERTY_ID = None
PROPERTY_TYPE = None
BOOKING_ID = None
PAYMENT_ID = None
PAYMENT_LINK = None
TRANSACTION_ID = None


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_response(response, show_body=True):
    """Print HTTP response details"""
    print(f"\nStatus Code: {response.status_code}")
    if show_body:
        try:
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
        except:
            print("Response Text:")
            print(response.text[:500])


def login(email=None, password=None):
    """Login and get access token"""
    print_section("Step 1: Login to Get JWT Token")
    
    if not email:
        print("\nEnter your login credentials:")
        email = input("Email: ").strip()
    
    if not password:
        password = getpass("Password: ").strip()
    
    url = f"{API_BASE}/auth/login/"
    data = {
        "email": email,
        "password": password
    }
    
    print(f"\nPOST {url}")
    print(f"Email: {email}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print_response(response)
        
        if response.status_code == 200:
            response_data = response.json()
            global ACCESS_TOKEN
            
            if 'tokens' in response_data:
                ACCESS_TOKEN = response_data['tokens'].get('access')
                print(f"\n✅ Login successful!")
                print(f"Access Token: {ACCESS_TOKEN[:50]}...")
                if 'user' in response_data:
                    user = response_data['user']
                    print(f"User: {user.get('full_name', user.get('username', 'N/A'))}")
                return True
            elif 'access' in response_data:
                ACCESS_TOKEN = response_data.get('access')
                print(f"\n✅ Login successful!")
                print(f"Access Token: {ACCESS_TOKEN[:50]}...")
                return True
            else:
                print("\n❌ Unexpected response format!")
                return False
        else:
            print("\n❌ Login failed!")
            if response.status_code == 400:
                try:
                    errors = response.json().get('errors', {})
                    print("Errors:", json.dumps(errors, indent=2))
                except:
                    pass
            return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to server at {BASE_URL}")
        print("Make sure Django server is running!")
        return False
    except Exception as e:
        print(f"\n❌ Login error: {str(e)}")
        return False


def get_headers():
    """Get request headers with auth token"""
    if not ACCESS_TOKEN:
        return {}
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }


def get_properties(property_type=None):
    """Get available properties"""
    print_section("Step 2: Get Available Properties")
    
    url = f"{API_BASE}/properties/"
    params = {}
    
    if property_type:
        params['property_type'] = property_type
    
    print(f"\nGET {url}")
    if params:
        print(f"Params: {params}")
    
    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            count = data.get('count', len(results))
            
            print(f"\n✅ Found {count} property/properties")
            
            if results:
                print("\n📋 Available Properties:")
                print("-" * 70)
                for i, prop in enumerate(results[:10], 1):  # Show first 10
                    prop_type = prop.get('property_type', {})
                    prop_type_name = prop_type.get('name', 'N/A') if isinstance(prop_type, dict) else 'N/A'
                    
                    print(f"\n{i}. {prop.get('title', 'N/A')}")
                    print(f"   ID: {prop.get('id')}")
                    print(f"   Type: {prop_type_name}")
                    print(f"   Status: {prop.get('status', 'N/A')}")
                    if prop.get('price'):
                        print(f"   Price: TZS {prop.get('price'):,.0f}")
                    if prop.get('address'):
                        print(f"   Address: {prop.get('address')}")
                
                # Select first available property
                global PROPERTY_ID, PROPERTY_TYPE
                selected = results[0]
                PROPERTY_ID = selected.get('id')
                PROPERTY_TYPE = prop_type_name.lower() if prop_type_name else None
                
                print(f"\n✅ Using Property:")
                print(f"   ID: {PROPERTY_ID}")
                print(f"   Name: {selected.get('title', 'N/A')}")
                print(f"   Type: {PROPERTY_TYPE}")
                
                return True
            else:
                print("\n⚠️  No properties found!")
                print("💡 Create a property first (hotel, house, lodge, etc.)")
                return False
        else:
            print(f"\n❌ Failed to get properties! (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"\n❌ Error getting properties: {str(e)}")
        return False


def create_booking():
    """Create a booking for the selected property"""
    print_section("Step 3: Create Booking")
    
    if not PROPERTY_ID:
        print("❌ No property ID available!")
        return False
    
    # Get property details first to understand structure
    try:
        prop_url = f"{API_BASE}/properties/{PROPERTY_ID}/"
        prop_response = requests.get(prop_url, headers=get_headers(), timeout=10)
        if prop_response.status_code == 200:
            property_data = prop_response.json()
            print(f"\n📋 Property Details:")
            print(f"   Title: {property_data.get('title', 'N/A')}")
            print(f"   Type: {PROPERTY_TYPE}")
    except:
        pass
    
    # First, try to get existing bookings for this property
    print("\n💡 Checking for existing bookings...")
    try:
        # Try to get bookings via properties web API (not REST API)
        # Since there's no direct API endpoint, we'll try to use existing bookings
        # or create via the web API endpoint
        pass
    except:
        pass
    
    # Try to create booking via the properties web API endpoint
    # This uses the properties/api/create-booking/ endpoint
    check_in = datetime.now().date() + timedelta(days=1)
    check_out = check_in + timedelta(days=3)  # 3 days booking
    
    # Use the web API endpoint (not REST API)
    url = f"{BASE_URL}/properties/api/create-booking/"
    
    booking_data = {
        "customer_name": "Test Customer",
        "phone": "+255712345678",
        "email": "test@example.com",
        "check_in_date": str(check_in),
        "check_out_date": str(check_out),
        "number_of_guests": 2,
    }
    
    # For hotels, add room info if needed
    if PROPERTY_TYPE == 'hotel':
        booking_data['room_type'] = 'Standard'
        booking_data['room_number'] = '101'  # Default room
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(booking_data, indent=2)}")
    print("\n⚠️  Note: This uses the web API endpoint which requires form data")
    
    try:
        # Try as JSON first
        response = requests.post(url, json=booking_data, headers=get_headers(), timeout=10)
        print_response(response)
        
        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                global BOOKING_ID
                BOOKING_ID = response_data.get('id') or response_data.get('booking_id')
                
                if BOOKING_ID:
                    print(f"\n✅ Booking created successfully!")
                    print(f"   Booking ID: {BOOKING_ID}")
                    return True
            except:
                # Response might be HTML or different format
                print("\n⚠️  Response is not JSON format")
                pass
        
        # If JSON failed, try form data
        print("\n💡 Trying with form data...")
        headers_form = get_headers()
        headers_form['Content-Type'] = 'application/x-www-form-urlencoded'
        
        response = requests.post(url, data=booking_data, headers=headers_form, timeout=10)
        print_response(response)
        
        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                BOOKING_ID = response_data.get('id') or response_data.get('booking_id')
                if BOOKING_ID:
                    print(f"\n✅ Booking created successfully!")
                    print(f"   Booking ID: {BOOKING_ID}")
                    return True
            except:
                pass
        
        print("\n❌ Failed to create booking via API")
        print("💡 Trying alternative: use existing booking...")
        return create_booking_alternative()
        
    except Exception as e:
        print(f"\n❌ Error creating booking: {str(e)}")
        print("💡 Trying alternative: use existing booking...")
        return create_booking_alternative()


def create_booking_alternative():
    """Alternative method: use existing booking or prompt user"""
    print("\n📝 Looking for existing bookings...")
    
    # Since we can't easily create bookings via API, let's prompt user
    print("\n💡 Booking creation via API is complex (requires property selection, rooms, etc.)")
    print("   Please provide an existing booking ID, or we'll try to find one.")
    
    # Try to get booking status endpoint (if booking ID is known)
    booking_id_input = input("\nEnter existing Booking ID (or press Enter to skip): ").strip()
    
    if booking_id_input:
        try:
            booking_id = int(booking_id_input)
            # Verify booking exists
            booking_url = f"{API_BASE}/bookings/{booking_id}/details/"
            response = requests.get(booking_url, headers=get_headers(), timeout=10)
            
            if response.status_code == 200:
                global BOOKING_ID
                BOOKING_ID = booking_id
                booking_data = response.json()
                print(f"\n✅ Found booking!")
                print(f"   Booking ID: {BOOKING_ID}")
                print(f"   Reference: {booking_data.get('booking_reference', 'N/A')}")
                print(f"   Total Amount: TZS {booking_data.get('total_amount', 0):,.0f}")
                return True
            else:
                print(f"\n❌ Booking {booking_id} not found!")
                return False
        except ValueError:
            print("\n❌ Invalid booking ID!")
            return False
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return False
    else:
        print("\n⚠️  No booking ID provided")
        print("💡 To test payment:")
        print("   1. Create a booking manually via admin panel:")
        print("      - Go to Properties → Hotels/Houses → Bookings")
        print("      - Create a new booking")
        print("   2. Run this script again and provide the Booking ID")
        print("   3. Or use the rent invoice test script: python test_azam_pay.py")
        return False


def create_payment_for_booking():
    """Create a payment for the booking"""
    print_section("Step 4: Create Payment for Booking")
    
    if not BOOKING_ID:
        print("❌ No booking ID available!")
        return False
    
    # Get booking details to get amount
    booking_amount = 50000.00  # Default
    try:
        # Use the correct booking details API endpoint
        booking_url = f"{API_BASE}/bookings/{BOOKING_ID}/details/"
        booking_response = requests.get(booking_url, headers=get_headers(), timeout=10)
        
        if booking_response.status_code == 200:
            booking_data = booking_response.json()
            booking_amount = float(booking_data.get('total_amount', 50000))
            print(f"\n📋 Booking Details:")
            print(f"   Booking Reference: {booking_data.get('booking_reference', 'N/A')}")
            print(f"   Total Amount: TZS {booking_amount:,.0f}")
            print(f"   Paid Amount: TZS {booking_data.get('payments', [{}])[0].get('amount', 0) if booking_data.get('payments') else 0:,.0f}")
            print(f"   Status: {booking_data.get('booking_status_display', 'N/A')}")
        else:
            print(f"\n⚠️  Could not fetch booking details (Status: {booking_response.status_code})")
            print(f"   Using default amount: TZS {booking_amount:,.0f}")
    except Exception as e:
        print(f"\n⚠️  Could not fetch booking details: {str(e)}")
        print(f"   Using default amount: TZS {booking_amount:,.0f}")
    
    # Create payment using unified Payment model
    # First, we need to get the current user's ID for tenant field
    url = f"{API_BASE}/payments/payments/"
    
    payment_data = {
        "booking": BOOKING_ID,
        "amount": str(booking_amount),
        "payment_method": "online",
        "status": "pending"
    }
    
    print(f"\nPOST {url}")
    print(f"Data: {json.dumps(payment_data, indent=2)}")
    
    try:
        response = requests.post(url, json=payment_data, headers=get_headers(), timeout=10)
        print_response(response)
        
        if response.status_code in [200, 201]:
            global PAYMENT_ID
            response_data = response.json()
            PAYMENT_ID = response_data.get('id')
            
            if PAYMENT_ID:
                print(f"\n✅ Payment created successfully!")
                print(f"   Payment ID: {PAYMENT_ID}")
                print(f"   Amount: TZS {booking_amount:,.0f}")
                return True
            else:
                print("\n⚠️  Payment created but no ID returned")
                print("Response:", json.dumps(response_data, indent=2))
                # Try to extract ID from response
                if 'payment_id' in response_data:
                    PAYMENT_ID = response_data.get('payment_id')
                    return True
                return False
        else:
            print("\n❌ Failed to create payment!")
            print("💡 Note: If this fails, you may need to create payment manually via admin")
            return False
    except Exception as e:
        print(f"\n❌ Error creating payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def initiate_gateway_payment():
    """Initiate gateway payment via AZAM Pay"""
    print_section("Step 5: Initiate AZAM Pay Payment")
    
    if not PAYMENT_ID:
        print("❌ No payment ID available!")
        return False
    
    # Try different endpoints for initiating gateway payment
    endpoints = [
        f"{API_BASE}/payments/payments/{PAYMENT_ID}/initiate/",
        f"{API_BASE}/rent/payments/{PAYMENT_ID}/initiate-gateway/",
    ]
    
    for url in endpoints:
        print(f"\nPOST {url}")
        print("⏳ Calling AZAM Pay API...")
        
        try:
            response = requests.post(url, headers=get_headers(), timeout=30)
            print_response(response)
            
            if response.status_code in [200, 201]:
                data = response.json()
                global PAYMENT_LINK, TRANSACTION_ID
                
                # Handle different response formats
                PAYMENT_LINK = data.get('payment_link') or data.get('redirect_url')
                TRANSACTION_ID = data.get('transaction_id') or data.get('id')
                transaction_ref = data.get('transaction_reference') or data.get('reference')
                
                print(f"\n✅ Payment initiated successfully!")
                print(f"Payment ID: {PAYMENT_ID}")
                if TRANSACTION_ID:
                    print(f"Transaction ID: {TRANSACTION_ID}")
                if transaction_ref:
                    print(f"Transaction Reference: {transaction_ref}")
                if PAYMENT_LINK:
                    print(f"\n🔗 Payment Link:")
                    print(f"   {PAYMENT_LINK}")
                    print(f"\n📝 Next Steps:")
                    print(f"   1. The payment link will open in your browser")
                    print(f"   2. Complete the payment on AZAM Pay sandbox")
                    print(f"   3. After payment, we'll verify the status")
                    
                    open_link = input("\nOpen payment link in browser? (y/n): ").strip().lower()
                    if open_link == 'y':
                        try:
                            webbrowser.open(PAYMENT_LINK)
                            print("✅ Payment link opened in browser!")
                        except Exception as e:
                            print(f"⚠️  Could not open browser: {e}")
                            print(f"   Please manually open: {PAYMENT_LINK}")
                    return True
                else:
                    print("\n⚠️  No payment link returned!")
                    print("Response:", json.dumps(data, indent=2))
                    # Continue to next endpoint
                    continue
            else:
                print(f"\n⚠️  Endpoint returned status {response.status_code}")
                if response.status_code == 404:
                    # Try next endpoint
                    continue
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        print("Error details:", json.dumps(error_data, indent=2))
                    except:
                        pass
                    # Don't try next endpoint if it's a validation error
                    break
        except requests.exceptions.Timeout:
            print("\n❌ Request timed out!")
            continue
        except Exception as e:
            print(f"\n⚠️  Error with endpoint: {str(e)}")
            continue
    
    print("\n❌ Failed to initiate gateway payment with all endpoints!")
    print("💡 Check:")
    print("   - Server logs for detailed errors")
    print("   - Payment ID is correct")
    print("   - Payment supports gateway initiation")
    return False


def verify_payment():
    """Verify payment status"""
    print_section("Step 6: Verify Payment Status")
    
    if not PAYMENT_ID:
        print("❌ No payment ID available!")
        return False
    
    url = f"{API_BASE}/rent/payments/{PAYMENT_ID}/verify/"
    print(f"POST {url}")
    print("\n⏳ Verifying payment with AZAM Pay...")
    
    try:
        response = requests.post(url, headers=get_headers(), timeout=30)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            verified = data.get('verified')
            transaction_status = data.get('transaction_status')
            
            print(f"\n✅ Payment verification complete!")
            print(f"Payment Status: {status}")
            print(f"Transaction Status: {transaction_status}")
            print(f"Verified: {verified}")
            
            if status == 'completed' and verified:
                print("\n🎉 Payment completed successfully!")
            elif status == 'pending':
                print("\n⏳ Payment is still pending. Wait a moment and try again.")
            else:
                print(f"\n⚠️  Payment status: {status}")
            
            return True
        else:
            print("\n❌ Failed to verify payment!")
            return False
    except Exception as e:
        print(f"\n❌ Verification error: {str(e)}")
        return False


def get_transactions():
    """Get all transactions"""
    print_section("Step 7: View Payment Transactions")
    
    url = f"{API_BASE}/payments/transactions/"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            count = data.get('count', len(results))
            
            print(f"\n✅ Found {count} transaction(s)")
            
            if results:
                print("\n📋 Recent Transactions:")
                print("-" * 70)
                for i, txn in enumerate(results[:5], 1):
                    print(f"\n{i}. Transaction #{txn.get('id')}")
                    print(f"   Payment ID: {txn.get('payment')}")
                    print(f"   Status: {txn.get('status', 'N/A')}")
                    if txn.get('gateway_transaction_id'):
                        print(f"   Gateway ID: {txn.get('gateway_transaction_id')}")
                    if txn.get('azam_reference'):
                        print(f"   AZAM Ref: {txn.get('azam_reference')}")
            
            return True
        else:
            print(f"\n❌ Failed to get transactions! (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"\n❌ Error getting transactions: {str(e)}")
        return False


def main():
    """Main test flow"""
    print("\n" + "=" * 70)
    print("  🏨 Property Booking Payment Test via AZAM Pay (Sandbox)")
    print("=" * 70)
    print(f"\n📍 Testing against: {BASE_URL}")
    print("📋 Make sure:")
    print("   1. Django server is running")
    print("   2. AZAM Pay credentials are in .env file")
    print("   3. You have properties in the database")
    print("   4. User has a phone number in profile")
    
    # Login
    print("\n" + "-" * 70)
    print("🔑 Authentication")
    print("-" * 70)
    
    if not login():
        print("\n❌ Cannot proceed without login. Exiting.")
        sys.exit(1)
    
    # Get properties
    if not get_properties():
        print("\n⚠️  Cannot proceed without properties.")
        print("💡 Create a property first (hotel, house, lodge, etc.)")
        sys.exit(1)
    
    # Create booking
    if not create_booking():
        print("\n⚠️  Could not create booking.")
        print("💡 You may need to create a booking manually first")
        sys.exit(1)
    
    # Create payment
    if not create_payment_for_booking():
        print("\n❌ Cannot proceed without payment. Exiting.")
        sys.exit(1)
    
    # Initiate gateway
    print("\n" + "=" * 70)
    print("🚀 Initiating AZAM Pay Payment...")
    print("=" * 70)
    
    if not initiate_gateway_payment():
        print("\n⚠️  Gateway initiation failed.")
        print("💡 Check server logs and credentials")
        sys.exit(1)
    
    # Wait and verify
    if PAYMENT_LINK:
        print("\n" + "=" * 70)
        print("⏳ Waiting for payment completion...")
        print("=" * 70)
        
        print(f"\n📱 Complete the payment on AZAM Pay sandbox")
        print(f"   Link: {PAYMENT_LINK}")
        
        wait_time = input("\n⏱️  How many seconds to wait before verification? (default: 30): ").strip()
        try:
            wait_seconds = int(wait_time) if wait_time else 30
        except:
            wait_seconds = 30
        
        print(f"\n⏳ Waiting {wait_seconds} seconds...")
        for i in range(wait_seconds, 0, -5):
            print(f"   {i} seconds remaining...", end='\r')
            time.sleep(min(5, i))
        print("\n")
    
    # Verify payment
    print("\n" + "=" * 70)
    verify = input("🔍 Verify payment status with AZAM Pay? (y/n): ").strip().lower()
    if verify == 'y':
        verify_payment()
    
    # Show transactions
    print("\n" + "=" * 70)
    get_transactions()
    
    # Final summary
    print("\n" + "=" * 70)
    print("  ✅ Test Complete!")
    print("=" * 70)
    print("\n📊 View Results:")
    print(f"   🌐 Phoenix Admin: {BASE_URL}/payments/transactions/")
    print(f"   🔗 API: {API_BASE}/payments/transactions/")
    
    if PAYMENT_ID:
        print(f"\n💡 Payment ID: {PAYMENT_ID}")
    if BOOKING_ID:
        print(f"💡 Booking ID: {BOOKING_ID}")
    if TRANSACTION_ID:
        print(f"💡 Transaction ID: {TRANSACTION_ID}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
