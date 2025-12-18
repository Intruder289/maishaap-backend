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
    AZAM_PAY_CONFIG = {
        'client_id': getattr(settings, 'AZAM_PAY_CLIENT_ID', ''),
        'client_secret': getattr(settings, 'AZAM_PAY_CLIENT_SECRET', ''),
        'api_key': getattr(settings, 'AZAM_PAY_API_KEY', ''),
        'app_name': getattr(settings, 'AZAM_PAY_APP_NAME', 'Maisha Property Management'),
        'base_url': getattr(settings, 'AZAM_PAY_BASE_URL', 'https://sandbox.azampay.co.tz'),
        'production_url': getattr(settings, 'AZAM_PAY_PRODUCTION_URL', 'https://api.azampay.co.tz'),
        'sandbox': getattr(settings, 'AZAM_PAY_SANDBOX', True),
        'webhook_secret': getattr(settings, 'AZAM_PAY_WEBHOOK_SECRET', ''),
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
        Uses clientId, clientSecret, apiKey, and appName
        
        Returns:
            str: Access token
        """
        # Check if we have a valid cached token
        if cls._access_token and cls._token_expires_at:
            if timezone.now() < cls._token_expires_at:
                return cls._access_token
        
        try:
            url = f"{cls.get_base_url()}/api/v1/Token/GetToken"
            
            payload = {
                "appName": cls.AZAM_PAY_CONFIG['app_name'],
                "clientId": cls.AZAM_PAY_CONFIG['client_id'],
                "clientSecret": cls.AZAM_PAY_CONFIG['client_secret'],
                "grantType": "client_credentials"
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": cls.AZAM_PAY_CONFIG['api_key']
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache token (typically expires in 1 hour)
            cls._access_token = data.get('data', {}).get('accessToken') or data.get('accessToken')
            # Assume token expires in 1 hour (adjust based on actual response)
            from datetime import timedelta
            cls._token_expires_at = timezone.now() + timedelta(hours=1)
            
            logger.info("AZAM Pay access token obtained successfully")
            return cls._access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get AZAM Pay access token: {str(e)}")
            raise Exception(f"Failed to authenticate with AZAM Pay: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting AZAM Pay token: {str(e)}")
            raise
    
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
            
            # Get user phone number
            user_profile = getattr(payment.tenant, 'profile', None)
            phone_number = user_profile.phone if user_profile and user_profile.phone else None
            
            if not phone_number:
                return {
                    'success': False,
                    'payment_link': None,
                    'transaction_id': None,
                    'reference': None,
                    'error': 'User phone number is required for payment'
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
            if not callback_url:
                from django.conf import settings
                base_domain = getattr(settings, 'BASE_URL', 'https://yourdomain.com')
                callback_url = f"{base_domain}/api/v1/payments/webhook/azam-pay/"
            
            # Generate reference
            reference = f"RENT-{payment.id}-{int(timezone.now().timestamp())}"
            
            # Choose endpoint based on payment method
            if payment_method == 'bank':
                # Bank checkout
                url = f"{base_url}/api/v1/bank/checkout"
                payload = {
                    "accountNumber": phone,  # Account number for bank
                    "accountName": payment.tenant.get_full_name() or payment.tenant.username,
                    "amount": str(payment.amount),
                    "currency": "TZS",
                    "referenceId": reference,
                    "redirectUrl": callback_url,
                    "cancelUrl": callback_url,
                    "merchantAccountNumber": cls.AZAM_PAY_CONFIG.get('merchant_account', ''),
                    "merchantMobileNumber": phone,
                    "merchantName": cls.AZAM_PAY_CONFIG['app_name'],
                    "paymentProvider": "CRDB",  # Default, can be configured
                    "additionalProperties": {
                        "payment_id": payment.id,
                        "invoice_id": payment.rent_invoice.id if payment.rent_invoice else None,
                        "tenant_id": payment.tenant.id,
                    }
                }
            else:
                # Mobile Money Operator (MNO) checkout
                url = f"{base_url}/api/v1/azampay/mno/checkout"
                payload = {
                    "vendorId": cls.AZAM_PAY_CONFIG.get('vendor_id', ''),
                    "vendorName": cls.AZAM_PAY_CONFIG['app_name'],
                    "amount": str(payment.amount),
                    "currency": "TZS",
                    "customerPhoneNumber": phone,
                    "merchantAccountNumber": cls.AZAM_PAY_CONFIG.get('merchant_account', ''),
                    "merchantMobileNumber": phone,
                    "merchantName": cls.AZAM_PAY_CONFIG['app_name'],
                    "referenceId": reference,
                    "redirectUrl": callback_url,
                    "cancelUrl": callback_url,
                    "additionalProperties": {
                        "payment_id": payment.id,
                        "invoice_id": payment.rent_invoice.id if payment.rent_invoice else None,
                        "tenant_id": payment.tenant.id,
                    }
                }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-API-Key": cls.AZAM_PAY_CONFIG['api_key']
            }
            
            # Make API call
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response (structure may vary, adjust based on actual response)
            success = data.get('success', False) or data.get('status') == 'success'
            
            if success:
                # Extract payment link and transaction ID
                payment_link = data.get('data', {}).get('redirectUrl') or data.get('redirectUrl') or data.get('paymentUrl')
                transaction_id = data.get('data', {}).get('transactionId') or data.get('transactionId') or data.get('id')
                
                return {
                    'success': True,
                    'payment_link': payment_link,
                    'transaction_id': transaction_id or reference,
                    'reference': reference,
                    'error': None
                }
            else:
                error_msg = data.get('message') or data.get('error') or 'Payment initiation failed'
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
            
            transaction_id = (
                transaction_data.get('transactionId') or
                transaction_data.get('transaction_id') or
                transaction_data.get('id') or
                transaction_data.get('referenceId')
            )
            
            reference = (
                transaction_data.get('referenceId') or
                transaction_data.get('reference') or
                transaction_data.get('ref') or
                transaction_id
            )
            
            status = transaction_data.get('status', '').lower()
            
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
