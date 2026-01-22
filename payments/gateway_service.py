"""
Payment Gateway Service for AZAM Pay Integration

This service handles communication with AZAM Pay payment gateway.
Based on AZAM Pay API documentation: https://developerdocs.azampay.co.tz/redoc

Key Features:
- Token-based authentication
- Mobile Money Operator (MNO) checkout
- Bank checkout
- Payment verification
- Webhook handling
"""

import requests
import json
import hmac
import hashlib
import base64
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class AZAMPayGateway:
    """
    AZAM Pay Payment Gateway Integration
    
    This class handles all interactions with AZAM Pay API.
    Based on official AZAM Pay documentation.
    """
    
    # Configuration
    _client_id = getattr(settings, 'AZAM_PAY_CLIENT_ID', '')
    _client_secret = getattr(settings, 'AZAM_PAY_CLIENT_SECRET', '')
    _api_key = getattr(settings, 'AZAM_PAY_API_KEY', '')
    _webhook_secret = getattr(settings, 'AZAM_PAY_WEBHOOK_SECRET', '')
    _sandbox = getattr(settings, 'AZAM_PAY_SANDBOX', True)
    # Pre-generated token from AZAMpay dashboard (for sandbox testing)
    _dashboard_token = getattr(settings, 'AZAM_PAY_TOKEN', '')
    
    AZAM_PAY_CONFIG = {
        'client_id': _client_id,
        'client_secret': _client_secret,
        # In sandbox mode, fallback to Client ID if API Key not provided
        'api_key': _api_key or (_client_id if _sandbox else ''),
        'app_name': getattr(settings, 'AZAM_PAY_APP_NAME', 'Maisha Property Management'),
        'base_url': getattr(settings, 'AZAM_PAY_BASE_URL', 'https://sandbox.azampay.co.tz'),
        'production_url': getattr(settings, 'AZAM_PAY_PRODUCTION_URL', 'https://api.azampay.co.tz'),
        'checkout_base_url': getattr(settings, 'AZAM_PAY_CHECKOUT_BASE_URL', 'https://checkout.azampay.co.tz'),
        'authenticator_base_url': getattr(settings, 'AZAM_PAY_AUTHENTICATOR_BASE_URL', 'https://authenticator.azampay.co.tz'),
        'sandbox': _sandbox,
        # In sandbox mode, fallback to Client Secret if Webhook Secret not provided
        'webhook_secret': _webhook_secret or (_client_secret if _sandbox else ''),
        # Pre-generated token from dashboard (preferred for sandbox)
        'dashboard_token': _dashboard_token,
        # Test phone number for sandbox testing
        'test_phone': getattr(settings, 'AZAM_PAY_TEST_PHONE', None),
    }
    
    # Token cache (in production, use Redis or similar)
    _access_token = None
    _token_expires_at = None
    
    @classmethod
    def get_base_url(cls):
        """Get base URL based on environment"""
        if cls.AZAM_PAY_CONFIG['sandbox']:
            return cls.AZAM_PAY_CONFIG['base_url']
        return cls.AZAM_PAY_CONFIG['production_url']
    
    @classmethod
    def get_access_token(cls):
        """
        Get access token from AZAM Pay
        
        For Sandbox Mode:
        - If AZAM_PAY_TOKEN is provided (pre-generated from dashboard), use it directly
        - Otherwise, try authenticator endpoint: https://authenticator-sandbox.azampay.co.tz/oauth/token
        
        For Production:
        - Always get token via API
        
        Returns:
            str: Access token
        """
        # For sandbox: Dashboard tokens might not work for checkout endpoints
        # Checkout endpoints require OAuth JWT tokens, not dashboard tokens
        # Only use dashboard token if we don't have OAuth credentials
        # Otherwise, always get OAuth token for checkout operations
        if cls.AZAM_PAY_CONFIG['sandbox'] and cls.AZAM_PAY_CONFIG['dashboard_token']:
            # Check if we have OAuth credentials - if yes, prefer OAuth token
            if cls.AZAM_PAY_CONFIG.get('client_id') and cls.AZAM_PAY_CONFIG.get('client_secret'):
                logger.info("OAuth credentials available - will get OAuth token (dashboard token not used for checkout)")
                # Don't use dashboard token, continue to OAuth flow
            else:
                # No OAuth credentials, use dashboard token as fallback
                logger.info("No OAuth credentials - using dashboard token (may not work for checkout)")
                cls._access_token = cls.AZAM_PAY_CONFIG['dashboard_token']
                from datetime import timedelta
                cls._token_expires_at = timezone.now() + timedelta(days=365)
                return cls._access_token
        
        # Validate credentials for API-based token retrieval
        if not cls.AZAM_PAY_CONFIG['client_id']:
            raise Exception("AZAM_PAY_CLIENT_ID is not set in settings. Please add it to your .env file.")
        if not cls.AZAM_PAY_CONFIG['client_secret']:
            raise Exception("AZAM_PAY_CLIENT_SECRET is not set in settings. Please add it to your .env file.")
        if not cls.AZAM_PAY_CONFIG['app_name']:
            raise Exception("AZAM_PAY_APP_NAME is not set in settings. Please add it to your .env file.")
        
        # Check if we have a valid cached token
        if cls._access_token and cls._token_expires_at:
            if timezone.now() < cls._token_expires_at:
                return cls._access_token
        
        # ✅ CORRECT TOKEN ENDPOINT: /AppRegistration/GenerateToken
        # According to AZAMpay API spec: https://developerdocs.azampay.co.tz/redoc
        # Endpoint: POST /AppRegistration/GenerateToken
        # Base URL: https://authenticator-sandbox.azampay.co.tz (sandbox) or https://authenticator.azampay.co.tz (production)
        if cls.AZAM_PAY_CONFIG['sandbox']:
            authenticator_base = "https://authenticator-sandbox.azampay.co.tz"
        else:
            # Use configured authenticator base URL for production
            authenticator_base = cls.AZAM_PAY_CONFIG.get('authenticator_base_url', 'https://authenticator.azampay.co.tz')
        authenticator_endpoints = [
            "/AppRegistration/GenerateToken",  # ✅ CORRECT - Official token endpoint
        ]
        
        # Also try endpoints on main sandbox URL
        endpoints = [
            "/api/v1/auth/token",
            "/api/token",
            "/api/v1/token",
            "/api/v1/Token/GetToken",
            "/api/v1/token/get-token",
            "/api/v1/oauth/token",
            "/api/Token/GetToken",
        ]
        
        base_url = cls.get_base_url()
        
        # ✅ CORRECT PAYLOAD FORMAT (Official AZAMpay API)
        # According to API spec: {"appName": "...", "clientId": "...", "clientSecret": "..."}
        # No grant_type needed - this is not standard OAuth2
        payload_variations = [
            # Format 1: Official format from API spec (try first)
            {
                "appName": cls.AZAM_PAY_CONFIG['app_name'],
                "clientId": cls.AZAM_PAY_CONFIG['client_id'],
                "clientSecret": cls.AZAM_PAY_CONFIG['client_secret']
            },
            # Format 2: Try without appName (fallback)
            {
                "clientId": cls.AZAM_PAY_CONFIG['client_id'],
                "clientSecret": cls.AZAM_PAY_CONFIG['client_secret']
            },
            # Format 3: Try with snake_case (fallback)
            {
                "app_name": cls.AZAM_PAY_CONFIG['app_name'],
                "client_id": cls.AZAM_PAY_CONFIG['client_id'],
                "client_secret": cls.AZAM_PAY_CONFIG['client_secret']
            },
        ]
        
        # Prepare headers - try with and without X-API-Key
        headers_variations = [
            {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-API-Key": cls.AZAM_PAY_CONFIG['api_key']
            },
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {cls.AZAM_PAY_CONFIG['api_key']}"
            },
            {
                "Content-Type": "application/json",
            }
        ]
        
        errors = []  # Collect all errors for better debugging
        
        # First, try authenticator endpoints (separate base URL)
        for endpoint in authenticator_endpoints:
            url = f"{authenticator_base}{endpoint}"
            for payload in payload_variations:
                for headers in headers_variations:
                    try:
                        logger.info(f"🔍 Trying AZAM Pay authenticator endpoint: {url}")
                        logger.debug(f"   Headers: {dict(headers)}")
                        payload_preview = {k: (v[:20] + '...' if isinstance(v, str) and len(v) > 20 else v) for k, v in payload.items()}
                        logger.debug(f"   Payload: {payload_preview}")
                        
                        response = requests.post(url, json=payload, headers=headers, timeout=30)
                        
                        logger.info(f"   Response: {response.status_code} {response.reason}")
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                logger.debug(f"   Response data: {json.dumps(data, indent=2)[:500]}")
                            except:
                                data = {'raw': response.text[:200]}
                                logger.warning(f"   Could not parse JSON response: {response.text[:200]}")
                            
                            # Parse token from response
                            # Response format from API spec: { "data": { "accessToken": "..." } } or { "accessToken": "..." }
                            cls._access_token = (
                                data.get('data', {}).get('accessToken') or
                                data.get('data', {}).get('access_token') or
                                data.get('accessToken') or
                                data.get('access_token') or
                                data.get('token') or
                                data.get('data', {}).get('token')
                            )
                            
                            # If still no token, try nested structures
                            if not cls._access_token and isinstance(data, dict):
                                for key in ['data', 'result', 'response']:
                                    if key in data and isinstance(data[key], dict):
                                        cls._access_token = (
                                            data[key].get('accessToken') or
                                            data[key].get('access_token') or
                                            data[key].get('token')
                                        )
                                        if cls._access_token:
                                            break
                            
                            if cls._access_token:
                                # Assume token expires in 1 hour (adjust based on actual response)
                                from datetime import timedelta
                                expires_in = data.get('expires_in', 3600)  # Default 1 hour
                                cls._token_expires_at = timezone.now() + timedelta(seconds=expires_in)
                                
                                logger.info(f"✅ AZAM Pay access token obtained successfully from authenticator endpoint")
                                return cls._access_token
                            else:
                                error_msg = f"Authenticator endpoint returned 200 but no token in response"
                                logger.warning(f"   {error_msg}: {data}")
                                errors.append(f"{url}: {error_msg}")
                        elif response.status_code == 404:
                            logger.debug(f"   Authenticator endpoint {endpoint} returned 404, trying next...")
                            continue
                        else:
                            try:
                                error_body = response.json()
                                error_msg = f"HTTP {response.status_code}: {json.dumps(error_body)}"
                            except:
                                error_body = response.text[:500] if response.text else "(empty response)"
                                error_msg = f"HTTP {response.status_code}: {error_body}"
                            
                            logger.warning(f"   ❌ {error_msg}")
                            payload_desc = f"payload={list(payload.keys())}"
                            header_desc = headers.get('X-API-Key', 'no-api-key')[:20] if headers.get('X-API-Key') else 'no-api-key'
                            errors.append(f"{url} ({payload_desc}, {header_desc}...): {error_msg}")
                            
                    except requests.exceptions.RequestException as e:
                        logger.debug(f"   Request error for authenticator endpoint: {str(e)}")
                        errors.append(f"{url}: {str(e)}")
                        continue
        
        # If authenticator endpoints failed, try main sandbox endpoints
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            for payload in payload_variations:
                for headers in headers_variations:
                    try:
                        logger.info(f"🔍 Trying AZAM Pay token endpoint: {url}")
                        logger.debug(f"   Headers: {dict(headers)}")
                        payload_preview = {k: (v[:20] + '...' if isinstance(v, str) and len(v) > 20 else v) for k, v in payload.items()}
                        logger.debug(f"   Payload: {payload_preview}")
                        
                        response = requests.post(url, json=payload, headers=headers, timeout=30)
                        
                        logger.info(f"   Response: {response.status_code} {response.reason}")
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                logger.debug(f"   Response data: {json.dumps(data, indent=2)[:500]}")
                            except:
                                data = {'raw': response.text[:200]}
                                logger.warning(f"   Could not parse JSON response: {response.text[:200]}")
                            
                            # Cache token (typically expires in 1 hour)
                            cls._access_token = data.get('data', {}).get('accessToken') or data.get('accessToken') or data.get('token')
                            if not cls._access_token:
                                # Try alternative response structures
                                if isinstance(data, dict):
                                    for key in ['access_token', 'accessToken', 'token', 'data']:
                                        if key in data:
                                            token_data = data[key]
                                            if isinstance(token_data, dict):
                                                cls._access_token = token_data.get('accessToken') or token_data.get('access_token') or token_data.get('token')
                                            elif isinstance(token_data, str):
                                                cls._access_token = token_data
                                            if cls._access_token:
                                                break
                            
                            if cls._access_token:
                                # Assume token expires in 1 hour (adjust based on actual response)
                                from datetime import timedelta
                                cls._token_expires_at = timezone.now() + timedelta(hours=1)
                                
                                logger.info(f"✅ AZAM Pay access token obtained successfully from {endpoint}")
                                return cls._access_token
                            else:
                                error_msg = f"Endpoint {endpoint} returned 200 but no token in response"
                                logger.warning(f"   {error_msg}: {data}")
                                errors.append(f"{url}: {error_msg}")
                        else:
                            # Capture all non-200 responses
                            try:
                                error_body = response.json()
                                error_msg = f"HTTP {response.status_code}: {json.dumps(error_body)}"
                            except:
                                error_body = response.text[:500] if response.text else "(empty response)"
                                error_msg = f"HTTP {response.status_code}: {error_body}"
                            
                            logger.warning(f"   ❌ {error_msg}")
                            payload_desc = f"payload={list(payload.keys())}"
                            header_desc = headers.get('X-API-Key', 'no-api-key')[:20] if headers.get('X-API-Key') else 'no-api-key'
                            errors.append(f"{url} ({payload_desc}, {header_desc}...): {error_msg}")
                        
                    except requests.exceptions.Timeout as e:
                        error_msg = f"Timeout connecting to {url}"
                        logger.error(f"   ⏱️  {error_msg}: {str(e)}")
                        errors.append(f"{url}: {error_msg}")
                    except requests.exceptions.ConnectionError as e:
                        error_msg = f"Connection error to {url}: {str(e)}"
                        logger.error(f"   🔌 {error_msg}")
                        errors.append(f"{url}: {error_msg}")
                    except requests.exceptions.RequestException as e:
                        error_msg = f"Request error: {str(e)}"
                        logger.error(f"   ❌ {error_msg}")
                        errors.append(f"{url}: {error_msg}")
                    except Exception as e:
                        error_msg = f"Unexpected error: {str(e)}"
                        logger.error(f"   💥 {error_msg}", exc_info=True)
                        errors.append(f"{url}: {error_msg}")
        
        # If all endpoints failed, raise error with helpful message
        total_attempts = len(endpoints) * len(payload_variations) * len(headers_variations)
        error_msg = f"Failed to authenticate with AZAM Pay. Tried {len(endpoints)} endpoint(s) × {len(payload_variations)} payload format(s) × {len(headers_variations)} header variation(s) = {total_attempts} total attempts.\n\n"
        
        if errors:
            error_msg += "Errors encountered:\n"
            for i, err in enumerate(errors[:10], 1):  # Show first 10 errors
                error_msg += f"  {i}. {err}\n"
            if len(errors) > 10:
                error_msg += f"  ... and {len(errors) - 10} more errors\n"
        else:
            error_msg += "No specific errors captured (all requests may have been skipped).\n"
        
        error_msg += "\nPlease check:\n"
        error_msg += "1. Your AZAM_PAY_CLIENT_ID and AZAM_PAY_CLIENT_SECRET in .env file\n"
        error_msg += f"2. Your AZAM_PAY_APP_NAME ('{cls.AZAM_PAY_CONFIG['app_name']}') matches the app name in AZAMpay dashboard\n"
        error_msg += f"3. Your AZAM_PAY_BASE_URL is correct ({base_url} for sandbox)\n"
        error_msg += "4. The endpoint URL in AZAMpay API documentation: https://developerdocs.azampay.co.tz/redoc\n"
        error_msg += "5. Your internet connection and AZAMpay sandbox availability\n"
        error_msg += f"6. Check server logs above for detailed request/response information"
        
        logger.error(error_msg)
        raise Exception(error_msg)
    
    @classmethod
    def initiate_payment(cls, payment, callback_url=None, payment_method='mobile_money'):
        """
        Initiate payment with AZAM Pay
        
        Supports:
        - Mobile Money Operator (MNO) checkout (M-Pesa, TigoPesa, AzamPesa, etc.)
        - Bank checkout
        
        Args:
            payment: Payment model instance
            callback_url: Webhook callback URL
            payment_method: 'mobile_money' or 'bank'
            
        Returns:
            dict: {
                'success': bool,
                'payment_link': str,  # URL to redirect user to
                'transaction_id': str,  # AZAM Pay transaction ID
                'reference': str,  # Reference number
                'error': str  # Error message if failed
            }
        """
        try:
            # Get access token
            access_token = cls.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': None,
                    'error': 'Failed to obtain access token'
                }
            
            # Get base URL
            base_url = cls.get_base_url()
            
            # Smart Logic: Select phone number based on user role
            # - Admin/Staff: Use customer phone (from booking) so customer receives payment prompt
            # - Customer: Use logged-in user's phone (their own profile phone)
            phone_number = None
            
            # Check if logged-in user is admin/staff
            is_admin_or_staff = payment.tenant.is_staff or payment.tenant.is_superuser
            
            if is_admin_or_staff and payment.booking:
                # Admin/Staff creating payment: Use customer phone
                # This ensures the customer receives the payment prompt
                phone_number = payment.booking.customer.phone if payment.booking.customer else None
                logger.info(f"[SMART LOGIC] Admin/Staff payment -> Using customer phone: {phone_number}")
                logger.info(f"[SMART LOGIC] Customer: {payment.booking.customer.full_name if payment.booking.customer else 'N/A'}")
                logger.info(f"[SMART LOGIC] Customer ID: {payment.booking.customer.id if payment.booking.customer else 'N/A'}")
            else:
                # Customer creating payment: Use their own profile phone
                user_profile = getattr(payment.tenant, 'profile', None)
                phone_number = user_profile.phone if user_profile and user_profile.phone else None
                logger.info(f"[SMART LOGIC] Customer payment -> Using tenant profile phone: {phone_number}")
                logger.info(f"[SMART LOGIC] Tenant: {payment.tenant.username}")
                logger.info(f"[SMART LOGIC] Tenant Profile ID: {user_profile.id if user_profile else 'No profile'}")
            
            # REMOVED: Fallback to tenant.phone attribute - this was causing wrong phone to be used
            # If phone is not found, we should fail with clear error message instead of using wrong phone
            
            if not phone_number:
                # Provide helpful error message based on user role
                if is_admin_or_staff and payment.booking:
                    error_msg = f'Phone number is required for payment. Customer ({payment.booking.customer.full_name if payment.booking.customer else "N/A"}) does not have a phone number. Please add a phone number to the customer profile.'
                else:
                    error_msg = f'Phone number is required for payment. Please add a phone number to your profile (User: {payment.tenant.username}).'
                
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': None,
                    'error': error_msg
                }
            
            # Normalize phone number (ensure it starts with country code)
            phone = phone_number.strip()
            if not phone.startswith('+'):
                # Assume Tanzania (+255) if no country code
                if phone.startswith('0'):
                    phone = '+255' + phone[1:]
                else:
                    phone = '+255' + phone
            
            # Prepare callback URL
            # For local testing, you can use ngrok or your production URL
            # The callback URL in AZAMpay dashboard should match what you use here
            if not callback_url:
                from django.conf import settings
                # Check if there's a specific webhook URL configured
                webhook_url = getattr(settings, 'AZAM_PAY_WEBHOOK_URL', None)
                if webhook_url:
                    callback_url = webhook_url
                else:
                    base_domain = getattr(settings, 'BASE_URL', 'https://yourdomain.com')
                    callback_url = f"{base_domain}/api/v1/payments/webhook/azam-pay/"
            
            logger.debug(f"   Using callback URL: {callback_url}")
            
            # Generate reference based on payment type
            if payment.booking:
                reference = f"BOOKING-{payment.booking.booking_reference}-{int(timezone.now().timestamp())}"
            elif payment.rent_invoice:
                reference = f"RENT-{payment.id}-{int(timezone.now().timestamp())}"
            else:
                reference = f"PAY-{payment.id}-{int(timezone.now().timestamp())}"
            
            # ✅ CORRECT ENDPOINT: Mobile Money Checkout
            # Official AZAMpay API endpoint for Mobile Money Operator checkout
            # Confirmed by AzamPay: https://checkout.azampay.co.tz/azampay/mno/checkout
            # Documentation: https://developerdocs.azampay.co.tz/redoc
            # Endpoint: POST /azampay/mno/checkout
            if cls.AZAM_PAY_CONFIG['sandbox']:
                checkout_base = base_url
            else:
                # Production: Use checkout.azampay.co.tz (confirmed by AzamPay)
                # AzamPay confirmed: https://checkout.azampay.co.tz/azampay/mno/checkout
                checkout_base = cls.AZAM_PAY_CONFIG.get('checkout_base_url', 'https://checkout.azampay.co.tz')
                logger.error(f"[AZAMPAY FIX] Using AzamPay confirmed endpoint: {checkout_base}/azampay/mno/checkout")
            
            checkout_url_endpoint = f"{checkout_base}/azampay/mno/checkout"
            
            # Format phone number: Must be exactly 12 digits starting with "2557" (E.164 format for Tanzania)
            # AZAMpay requires: 2557XXXXXXXX (exactly 12 digits, starting with 2557)
            # Remove all non-digit characters
            digits_only = ''.join(filter(str.isdigit, phone))
            
            # Remove leading zeros
            digits_only = digits_only.lstrip('0')
            
            # Extract mobile number part (should be 9 digits starting with 7)
            if digits_only.startswith('255'):
                # Remove 255 prefix to get mobile number
                mobile_part = digits_only[3:]
            elif digits_only.startswith('0'):
                # Remove leading 0
                mobile_part = digits_only[1:]
            else:
                # Assume it's already a mobile number
                mobile_part = digits_only
            
            # Ensure mobile part starts with 7 (Tanzanian mobile numbers start with 7)
            if not mobile_part.startswith('7'):
                # Try to find 7 in the number
                if '7' in mobile_part:
                    # Find first occurrence of 7 and take from there
                    idx = mobile_part.index('7')
                    mobile_part = mobile_part[idx:]
                else:
                    # If no 7 found, prepend 7
                    mobile_part = '7' + mobile_part
            
            # Take exactly 9 digits (mobile number part)
            if len(mobile_part) > 9:
                mobile_part = mobile_part[:9]
            elif len(mobile_part) < 9:
                # Pad with zeros if too short (shouldn't happen, but handle it)
                mobile_part = mobile_part.ljust(9, '0')
            
            # Construct final format: 255 + 9-digit mobile (must start with 7)
            if len(mobile_part) == 9 and mobile_part.startswith('7'):
                phone_number_clean = '255' + mobile_part
            else:
                # If format is invalid, log error and return error
                error_msg = f"Phone number '{phone}' could not be formatted correctly. Mobile part: '{mobile_part}' (must be 9 digits starting with 7). Original phone: {phone_number}"
                logger.error(f"[SMART LOGIC ERROR] {error_msg}")
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': None,
                    'error': f'Invalid phone number format: {phone}. Phone number must be a valid Tanzanian mobile number (e.g., 0758123456 or +255758123456).'
                }
            
            # Final validation: Must be exactly 12 digits starting with 2557
            if not (len(phone_number_clean) == 12 and phone_number_clean.startswith('2557')):
                error_msg = f"Phone number '{phone}' formatted to '{phone_number_clean}' doesn't match required format (2557XXXXXXXX). Original phone: {phone_number}"
                logger.error(f"[SMART LOGIC ERROR] {error_msg}")
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': None,
                    'error': f'Invalid phone number format: {phone}. Phone number must be a valid Tanzanian mobile number (e.g., 0758123456 or +255758123456).'
                }
            
            logger.info(f"[SMART LOGIC] Formatted phone number: {phone} -> {phone_number_clean}")
            logger.info(f"[SMART LOGIC] Phone source: {'Customer phone' if (is_admin_or_staff and payment.booking) else 'Tenant profile phone'}")
            logger.info(f"[SMART LOGIC] Account number to be sent to AzamPay: {phone_number_clean}")
            
            # Determine provider from payment model (customer selected) or default
            # Map our provider values to AzamPay's expected format
            # AzamPay expects: "Airtel", "Tigo", "Mpesa", "Halopesa", "Azampesa" (title case)
            # Our values are: "AIRTEL", "TIGO", "MPESA", "HALOPESA" (uppercase)
            provider_mapping = {
                'AIRTEL': 'Airtel',
                'TIGO': 'Tigo',
                'MPESA': 'Mpesa',
                'HALOPESA': 'Halopesa',
                'AZAMPESA': 'Azampesa',
                # Handle case variations
                'airtel': 'Airtel',
                'tigo': 'Tigo',
                'mpesa': 'Mpesa',
                'halopesa': 'Halopesa',
                'azampesa': 'Azampesa',
                'Airtel': 'Airtel',
                'Tigo': 'Tigo',
                'Mpesa': 'Mpesa',
                'Halopesa': 'Halopesa',
                'Azampesa': 'Azampesa',
            }
            
            if hasattr(payment, 'mobile_money_provider') and payment.mobile_money_provider:
                provider_raw = payment.mobile_money_provider.upper()
                provider = provider_mapping.get(provider_raw, 'Airtel')  # Default to Airtel if not found
                logger.error(f"[AZAMPAY FIX] Using customer-selected provider: {payment.mobile_money_provider} -> {provider}")
                print(f"[AZAMPAY FIX] Provider mapping: {payment.mobile_money_provider} -> {provider}")
            else:
                default_raw = cls.AZAM_PAY_CONFIG.get('default_provider', 'AIRTEL').upper()
                provider = provider_mapping.get(default_raw, 'Airtel')
                logger.error(f"[AZAMPAY FIX] Using default provider: {default_raw} -> {provider}")
                print(f"[AZAMPAY FIX] Provider mapping: {default_raw} -> {provider}")
            
            # Prepare redirect URL (success page)
            # Use callback URL as redirect if no separate redirect URL configured
            redirect_url = callback_url  # Can be customized to point to a success page
            
            # ✅ CORRECT PAYLOAD FORMAT (Official AzamPay REST API)
            # According to API spec: accountNumber (not phoneNumber), amount as number (not string)
            # Required fields: accountNumber, amount, currency, externalId, provider
            # Provider must be in title case: "Airtel", "Tigo", "Mpesa", "Halopesa", "Azampesa"
            payload = {
                "accountNumber": phone_number_clean,  # MSISDN/phone number (Format: "2557XXXXXXXX")
                "amount": int(float(payment.amount)),  # Amount as number (in TZS)
                "currency": "TZS",
                "externalId": reference,
                "provider": provider  # "Airtel", "Tigo", "Mpesa", "Halopesa", "Azampesa" (title case)
            }
            
            logger.info(f"[SMART LOGIC] Final payload accountNumber: {payload['accountNumber']}")
            logger.info(f"[SMART LOGIC] Phone source confirmation: {'Customer phone from booking' if (is_admin_or_staff and payment.booking) else 'Tenant profile phone'}")
            
            # Optional: Add additionalProperties if needed
            # payload["additionalProperties"] = {}
            
            # Headers (Official AzamPay format)
            # According to API spec code samples: 'X-API-Key' (uppercase) is required
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            # Add X-API-Key (uppercase as shown in API spec code samples)
            # Required for checkout endpoints
            api_key_value = cls.AZAM_PAY_CONFIG.get('api_key', '').strip()
            client_id_value = cls.AZAM_PAY_CONFIG.get('client_id', '').strip()
            
            if api_key_value:
                headers["X-API-Key"] = api_key_value
                logger.error("[AZAMPAY FIX] Using AZAM_PAY_API_KEY for X-API-Key header")
                print("[AZAMPAY FIX] Using AZAM_PAY_API_KEY for X-API-Key header")
            elif client_id_value:
                # Use client_id as X-API-Key fallback (works for both sandbox and production)
                # According to AzamPay docs, Client ID can be used as API Key
                headers["X-API-Key"] = client_id_value
                logger.error(f"[AZAMPAY FIX] Using CLIENT_ID as X-API-Key (API_KEY not set): {client_id_value[:20]}...")
                print(f"[AZAMPAY FIX] Using CLIENT_ID as X-API-Key (API_KEY not set): {client_id_value[:20]}...")
            else:
                logger.error("[AZAMPAY FIX] CRITICAL: No X-API-Key available - both API_KEY and CLIENT_ID are missing!")
                logger.error("[AZAMPAY FIX] This will cause 'Invalid Vendor' errors. Please set AZAM_PAY_API_KEY or AZAM_PAY_CLIENT_ID in .env")
                print("[AZAMPAY FIX] CRITICAL: No X-API-Key available!")
            
            # Make API call to AZAMpay Mobile Money Checkout endpoint
            try:
                print(f"\n[AZAMPAY CHECKOUT] Endpoint: {checkout_url_endpoint}")
                print(f"[AZAMPAY CHECKOUT] Payload: {json.dumps(payload, indent=2)}")
                print(f"[AZAMPAY CHECKOUT] Headers: Authorization=Bearer ***, X-API-Key={'***' if headers.get('X-API-Key') else 'none'}")
                
                logger.error(f"[AZAMPAY FIX] Calling checkout endpoint: {checkout_url_endpoint}")
                logger.error(f"[AZAMPAY FIX] Method: POST")
                logger.error(f"[AZAMPAY FIX] Token: {access_token[:50]}...")
                logger.error(f"[AZAMPAY FIX] Headers: Authorization=Bearer ***, X-API-Key={'***' if headers.get('X-API-Key') else 'NONE - THIS WILL FAIL!'}")
                logger.error(f"[AZAMPAY FIX] Payload: {json.dumps(payload, indent=2)}")
                print(f"[AZAMPAY FIX] Headers: X-API-Key={'SET' if headers.get('X-API-Key') else 'NOT SET - WILL FAIL!'}")
                
                # Make API call
                response = requests.post(checkout_url_endpoint, json=payload, headers=headers, timeout=30)
                
                print(f"[AZAMPAY CHECKOUT] Response: {response.status_code} {response.reason}")
                logger.info(f"   [AZAMPAY] Response: {response.status_code} {response.reason}")
                
                # Log response for debugging
                try:
                    response_data = response.json()
                    print(f"[AZAMPAY CHECKOUT] Response JSON: {json.dumps(response_data, indent=2)}")
                    logger.info(f"   [AZAMPAY] Response JSON: {json.dumps(response_data, indent=2)}")
                except:
                    response_text = response.text[:500] if response.text else "(empty response)"
                    print(f"[AZAMPAY CHECKOUT] Response text: {response_text}")
                    logger.warning(f"   [AZAMPAY] Response text: {response_text}")
                    logger.warning(f"   [AZAMPAY] Response headers: {dict(response.headers)}")
                
                # Check if successful (200 or 201)
                if response.status_code == 200 or response.status_code == 201:
                    try:
                        data = response.json()
                    except:
                        error_msg = f"Response returned {response.status_code} but response is not valid JSON: {response.text[:200]}"
                        logger.error(f"   ❌ {error_msg}")
                        return {
                            'success': False,
                            'payment_link': None,
                            'transaction_id': None,
                            'reference': reference,
                            'error': error_msg
                        }
                    
                    # Parse response according to AzamPay API format
                    # Actual response: { "success": true, "transactionId": "...", "message": "...", "messageCode": 0 }
                    success = data.get('success', False)
                    transaction_id = data.get('transactionId') or data.get('transaction_id')
                    message = data.get('message', '')
                    message_code = data.get('messageCode', 0)
                    
                    if success and transaction_id:
                        # For MNO checkout, payment is initiated directly on mobile money network
                        # The transactionId is used to track payment status
                        logger.info(f"✅ Payment checkout created successfully!")
                        logger.info(f"   Transaction ID: {transaction_id}")
                        logger.info(f"   Message: {message}")
                        logger.info(f"   Message Code: {message_code}")
                        
                        # MNO payments are processed directly - user receives prompt on their phone
                        # No redirect URL needed - payment happens on mobile money network
                        return {
                            'success': True,
                            'payment_link': None,  # MNO payments don't use redirect URLs
                            'transaction_id': transaction_id,
                            'reference': reference,
                            'message': message,
                            'message_code': message_code,
                            'error': None
                        }
                    else:
                        error_msg = f"Response returned {response.status_code} but success=false or no transactionId. Message: {message}, Data: {data}"
                        logger.error(f"   ❌ {error_msg}")
                        return {
                            'success': False,
                            'payment_link': None,
                            'transaction_id': transaction_id,
                            'reference': reference,
                            'error': error_msg or message
                        }
                else:
                    # Handle error responses
                    try:
                        error_data = response.json()
                        error_msg = f"HTTP {response.status_code}: {json.dumps(error_data)}"
                    except:
                        error_text = response.text[:200] if response.text else "(empty response)"
                        error_msg = f"HTTP {response.status_code}: {error_text}"
                    
                    logger.error(f"   ❌ {error_msg}")
                    return {
                        'success': False,
                        'payment_link': None,
                        'transaction_id': None,
                        'reference': reference,
                        'error': error_msg
                    }
                    
            except requests.exceptions.Timeout as e:
                error_msg = f"Request timed out: {str(e)}"
                logger.error(f"   ⏱️  {error_msg}")
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': reference,
                    'error': error_msg
                }
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: {str(e)}"
                logger.error(f"   🔌 {error_msg}")
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': reference,
                    'error': error_msg
                }
            except requests.exceptions.RequestException as e:
                error_msg = f"Request failed: {str(e)}"
                logger.error(f"   ❌ Request exception: {error_msg}")
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': reference,
                    'error': error_msg
                }
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"   💥 {error_msg}", exc_info=True)
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': reference,
                    'error': error_msg
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AZAM Pay API error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message') or error_data.get('error') or str(e)
                except:
                    error_msg = str(e)
            else:
                error_msg = str(e)
            
            return {
                'success': False,
                'payment_link': None,
                'transaction_id': None,
                'reference': None,
                'error': error_msg
            }
        except Exception as e:
            logger.error(f"Error initiating AZAM Pay payment: {str(e)}", exc_info=True)
            return {
                'success': False,
                'payment_link': None,
                'transaction_id': None,
                'reference': None,
                'error': str(e)
            }
    
    @classmethod
    def verify_payment(cls, transaction_id):
        """
        Verify payment status with AZAM Pay
        
        Args:
            transaction_id: AZAM Pay transaction ID or reference ID
            
        Returns:
            dict: {
                'success': bool,
                'status': str,  # 'successful', 'failed', 'pending'
                'amount': Decimal,
                'reference': str,
                'error': str
            }
        """
        try:
            # Get access token
            access_token = cls.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'status': None,
                    'amount': None,
                    'reference': None,
                    'error': 'Failed to obtain access token'
                }
            
            base_url = cls.get_base_url()
            
            # Query transaction status
            # Note: Endpoint may vary, adjust based on actual API
            url = f"{base_url}/api/v1/Transaction/Query"
            
            payload = {
                "referenceId": transaction_id
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-API-Key": cls.AZAM_PAY_CONFIG['api_key']
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            transaction_data = data.get('data', {}) or data
            
            status = transaction_data.get('status', '').lower()
            amount = transaction_data.get('amount')
            reference = transaction_data.get('referenceId') or transaction_id
            
            # Map AZAM Pay status to our status
            if status in ['success', 'successful', 'completed', 'paid']:
                status = 'successful'
            elif status in ['failed', 'failure', 'error', 'cancelled']:
                status = 'failed'
            else:
                status = 'pending'
            
            return {
                'success': True,
                'status': status,
                'amount': Decimal(str(amount)) if amount else None,
                'reference': reference,
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AZAM Pay verification error: {str(e)}")
            return {
                'success': False,
                'status': None,
                'amount': None,
                'reference': None,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error verifying AZAM Pay payment: {str(e)}", exc_info=True)
            return {
                'success': False,
                'status': None,
                'amount': None,
                'reference': None,
                'error': str(e)
            }
    
    @classmethod
    def verify_webhook_signature(cls, payload, signature):
        """
        Verify webhook signature from AZAM Pay
        
        Args:
            payload: Raw request body (bytes or string)
            signature: Signature from webhook header
            
        Returns:
            bool: True if signature is valid
        """
        try:
            if not signature:
                logger.warning("No signature provided in webhook")
                return False
            
            # Get webhook secret
            secret = cls.AZAM_PAY_CONFIG['webhook_secret']
            if not secret:
                logger.warning("Webhook secret not configured")
                # In development, you might want to allow this
                # In production, this should return False
                return cls.AZAM_PAY_CONFIG['sandbox']
            
            # Convert payload to bytes if string
            if isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            else:
                payload_bytes = payload
            
            # Generate expected signature using HMAC-SHA256
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures (use constant-time comparison)
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}", exc_info=True)
            return False
    
    @classmethod
    def parse_webhook_payload(cls, payload):
        """
        Parse webhook payload from AZAM Pay
        
        Args:
            payload: Webhook request body (dict or JSON string)
            
        Returns:
            dict: {
                'transaction_id': str,
                'reference': str,
                'status': str,
                'amount': Decimal,
                'payment_id': int,  # From metadata
            }
        """
        try:
            # If payload is string, parse it
            if isinstance(payload, str):
                payload = json.loads(payload)
            
            # Extract transaction data
            # Structure may vary, adjust based on actual webhook format
            transaction_data = payload.get('data', {}) or payload
            
            # AzamPay webhook uses 'transid' field (not 'transactionId')
            transaction_id = (
                transaction_data.get('transid') or  # AzamPay actual field name
                transaction_data.get('transactionId') or
                transaction_data.get('transaction_id') or
                transaction_data.get('id') or
                transaction_data.get('referenceId') or
                transaction_data.get('transId')  # Alternative casing
            )
            
            reference = (
                transaction_data.get('reference') or
                transaction_data.get('referenceId') or
                transaction_data.get('ref') or
                transaction_data.get('externalreference') or  # AzamPay field
                transaction_data.get('utilityref') or  # AzamPay external reference
                transaction_id
            )
            
            # AzamPay uses 'transactionstatus' field (not 'status')
            status = (
                transaction_data.get('transactionstatus') or  # AzamPay actual field name
                transaction_data.get('status') or
                transaction_data.get('transaction_status')
            )
            if status:
                status = status.lower()
            
            amount = transaction_data.get('amount')
            if amount:
                amount = Decimal(str(amount))
            else:
                amount = None
            
            # Get payment ID from metadata or additionalProperties
            metadata = transaction_data.get('metadata', {}) or transaction_data.get('additionalProperties', {})
            payment_id = metadata.get('payment_id')
            
            return {
                'transaction_id': transaction_id,
                'reference': reference,
                'status': status,
                'amount': amount,
                'payment_id': payment_id,
            }
            
        except Exception as e:
            logger.error(f"Error parsing webhook payload: {str(e)}", exc_info=True)
            return None


class PaymentGatewayService:
    """
    Main payment gateway service that routes to appropriate gateway
    """
    
    @staticmethod
    def get_gateway(provider_name):
        """Get gateway instance based on provider name"""
        if provider_name.lower() == 'azam pay' or provider_name.lower() == 'azampay':
            return AZAMPayGateway()
        # Add other gateways here in the future
        raise ValueError(f"Unsupported payment gateway: {provider_name}")
    
    @staticmethod
    def initiate_payment(payment, provider_name='azam pay', callback_url=None, payment_method='mobile_money'):
        """Initiate payment with specified gateway"""
        gateway = PaymentGatewayService.get_gateway(provider_name)
        return gateway.initiate_payment(payment, callback_url, payment_method)
    
    @staticmethod
    def verify_payment(transaction_id, provider_name='azam pay'):
        """Verify payment with specified gateway"""
        gateway = PaymentGatewayService.get_gateway(provider_name)
        return gateway.verify_payment(transaction_id)
    
    @staticmethod
    def verify_webhook_signature(payload, signature, provider_name='azam pay'):
        """Verify webhook signature"""
        gateway = PaymentGatewayService.get_gateway(provider_name)
        return gateway.verify_webhook_signature(payload, signature)
    
    @staticmethod
    def parse_webhook_payload(payload, provider_name='azam pay'):
        """Parse webhook payload"""
        gateway = PaymentGatewayService.get_gateway(provider_name)
        return gateway.parse_webhook_payload(payload)
