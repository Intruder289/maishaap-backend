from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
from . import models, serializers
from .gateway_service import PaymentGatewayService
from django.shortcuts import get_object_or_404
# Swagger documentation - using drf-spectacular
# Import extend_schema for explicit documentation
try:
    from drf_spectacular.utils import extend_schema, OpenApiParameter
    from drf_spectacular.types import OpenApiTypes
except ImportError:
    # Fallback if drf-spectacular is not available
    extend_schema = lambda *args, **kwargs: lambda func: func  # No-op decorator
    OpenApiParameter = None
    OpenApiTypes = None

# Provide no-op decorator for backward compatibility with existing @swagger_auto_schema decorators
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
except ImportError:
    # drf-yasg not installed, use drf-spectacular instead
    # Decorators will be ignored - drf-spectacular auto-discovers endpoints
    def swagger_auto_schema(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class openapi:
        class Response:
            def __init__(self, *args, **kwargs):
                pass
        class Schema:
            def __init__(self, *args, **kwargs):
                pass
        class Items:
            def __init__(self, *args, **kwargs):
                pass
        class Contact:
            def __init__(self, *args, **kwargs):
                pass
        class License:
            def __init__(self, *args, **kwargs):
                pass
        class Info:
            def __init__(self, *args, **kwargs):
                pass
        TYPE_OBJECT = 'object'
        TYPE_STRING = 'string'
        TYPE_INTEGER = 'integer'
        TYPE_NUMBER = 'number'
        TYPE_BOOLEAN = 'boolean'
        TYPE_ARRAY = 'array'
        FORMAT_EMAIL = 'email'
        FORMAT_DATE = 'date'
        FORMAT_DATETIME = 'date-time'
        FORMAT_DECIMAL = 'decimal'
        FORMAT_URI = 'uri'
        FORMAT_UUID = 'uuid'
        IN_QUERY = 'query'
        IN_PATH = 'path'
        IN_BODY = 'body'
        IN_FORM = 'formData'
        IN_HEADER = 'header'
        
        # Create a proper Parameter class that stores arguments
        class Parameter:
            def __init__(self, name, in_, description=None, type=None, required=False, **kwargs):
                self.name = name
                self.in_ = in_
                self.description = description or ''
                self.type = type or 'string'
                self.required = required
                # Store all kwargs for compatibility
                for key, value in kwargs.items():
                    setattr(self, key, value)
import json


class PaymentProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Payment Providers (Read-only)
    
    list: Get all payment providers
    retrieve: Get a specific payment provider
    """
    queryset = models.PaymentProvider.objects.all()
    serializer_class = serializers.PaymentProviderSerializer
    permission_classes = [permissions.IsAuthenticated]


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Invoice management
    
    list: Get all invoices (filtered by user role)
    retrieve: Get a specific invoice
    create: Create a new invoice
    update: Update an invoice
    partial_update: Partially update an invoice
    destroy: Delete an invoice
    """
    queryset = models.Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Tenants should see their invoices, staff can see all
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
            
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return super().get_queryset()
        return self.queryset.filter(tenant=user)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Payment management
    
    list: Get all payments (filtered by user role)
    retrieve: Get a specific payment
    create: Create a new payment (for booking payments - hotel, house, lodge, venue)
    update: Update a payment
    partial_update: Partially update a payment
    destroy: Delete a payment
    initiate_gateway: Initiate AZAM Pay gateway payment for booking
    """
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
            
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return super().get_queryset()
        return self.queryset.filter(tenant=user)
    
    def perform_create(self, serializer):
        """Set tenant to logged-in user when creating payment"""
        serializer.save(tenant=self.request.user, recorded_by=self.request.user)

    @swagger_auto_schema(
        method='post',
        operation_description="""
        Initiate payment with payment gateway (AZAM Pay) for booking payments.
        
        Works for all property types: hotel, house, lodge, venue.
        Uses smart phone logic to select correct phone number.
        
        **Mobile Money Provider:**
        - If `mobile_money_provider` was already set when creating the payment, it will be used automatically
        - If not set, you must pass it in the request body
        - Valid values: AIRTEL, TIGO, MPESA, HALOPESA
        
        **Flow:**
        1. Validates payment has booking
        2. Gets mobile money provider (from payment or request)
        3. Automatically sets payment provider to "AZAM Pay" if not set
        4. Calls AZAM Pay API with smart phone selection
        5. Creates PaymentTransaction
        6. Returns transaction details
        """,
        operation_summary="Initiate Gateway Payment for Booking",
        tags=['Payments'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'mobile_money_provider': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Mobile money provider (required if not already set on payment): AIRTEL, TIGO, MPESA, HALOPESA. If already set when creating payment, this is optional.',
                    enum=['AIRTEL', 'TIGO', 'MPESA', 'HALOPESA']
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Payment initiated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'transaction_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'transaction_reference': openapi.Schema(type=openapi.TYPE_STRING),
                        'gateway_transaction_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'phone_number_used': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number used for payment')
                    }
                )
            ),
            400: "Payment already completed, missing booking, or gateway error",
            404: "Payment not found",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    # CRITICAL: @extend_schema must be BEFORE @action for drf-spectacular
    @extend_schema(
        summary="Initiate Gateway Payment for Booking",
        description="""
        Initiate payment with payment gateway (AZAM Pay) for booking payments.
        
        Works for all property types: hotel, house, lodge, venue.
        Uses smart phone logic to select correct phone number.
        
        **Mobile Money Provider:**
        - If `mobile_money_provider` was already set when creating the payment, it will be used automatically
        - If not set, you must pass it in the request body
        - Valid values: AIRTEL, TIGO, MPESA, HALOPESA
        
        **Flow:**
        1. Validates payment has booking
        2. Gets mobile money provider (from payment or request)
        3. Automatically sets payment provider to "AZAM Pay" if not set
        4. Calls AZAM Pay API with smart phone selection
        5. Creates PaymentTransaction
        6. Returns transaction details
        """,
        tags=['Payments'],
        request={
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'mobile_money_provider': {
                            'type': 'string',
                            'description': 'Mobile money provider (required if not already set on payment): AIRTEL, TIGO, MPESA, HALOPESA. If already set when creating payment, this is optional.',
                            'enum': ['AIRTEL', 'TIGO', 'MPESA', 'HALOPESA']
                        }
                    }
                }
            }
        },
        responses={
            201: {
                'description': 'Payment initiated successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'success': {'type': 'boolean'},
                                'payment_id': {'type': 'integer'},
                                'transaction_id': {'type': 'integer'},
                                'transaction_reference': {'type': 'string'},
                                'gateway_transaction_id': {'type': 'string'},
                                'message': {'type': 'string'},
                                'phone_number_used': {'type': 'string', 'description': 'Phone number used for payment'},
                                'booking_reference': {'type': 'string'}
                            }
                        }
                    }
                }
            },
            400: {'description': 'Payment already completed, missing booking, or gateway error'},
            404: {'description': 'Payment not found'},
            401: {'description': 'Authentication required'}
        }
    )
    @action(detail=True, methods=['post'], url_path='initiate-gateway')
    def initiate_gateway(self, request, pk=None):
        """
        Initiate payment with payment gateway (AZAM Pay) for booking payments.
        
        Works for all property types: hotel, house, lodge, venue.
        Uses smart phone logic:
        - Admin/Staff: Uses customer phone from booking
        - Customer: Uses their own profile phone
        
        Flow:
        1. Validates payment has booking
        2. Gets mobile money provider from request (if mobile_money payment)
        3. Calls AZAM Pay API with smart phone selection
        4. Creates PaymentTransaction
        5. Returns transaction details to mobile app
        """
        payment = self.get_object()
        
        # Check if payment is already completed
        if payment.status == 'completed':
            return Response({
                'success': False,
                'error': 'Payment already completed',
                'message': f'This payment (ID: {payment.id}) has already been completed. No further action is needed.',
                'payment_id': payment.id,
                'status': payment.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate payment has booking (required for booking payments)
        if not payment.booking:
            return Response({
                'success': False,
                'error': 'Booking required',
                'message': 'This payment must be linked to a booking. This endpoint is for booking payments only. Please create a payment with a valid booking ID.',
                'payment_id': payment.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get mobile money provider if this is a mobile_money payment
        if payment.payment_method == 'mobile_money':
            # Check if mobile_money_provider is already set on the payment
            # If not, get it from request body
            mobile_money_provider = payment.mobile_money_provider
            if not mobile_money_provider:
                mobile_money_provider = request.data.get('mobile_money_provider', '').strip()
            
            # If still not set, return error
            if not mobile_money_provider:
                return Response({
                    'success': False,
                    'error': 'Mobile Money Provider required',
                    'message': 'Please select your mobile money provider. Choose one of: AIRTEL, TIGO, MPESA, or HALOPESA. You can pass it when creating the payment or when initiating the gateway payment.',
                    'valid_providers': ['AIRTEL', 'TIGO', 'MPESA', 'HALOPESA']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update payment with mobile money provider (normalize to uppercase)
            if payment.mobile_money_provider != mobile_money_provider.upper():
                payment.mobile_money_provider = mobile_money_provider.upper()
                payment.save()
        
        # Get or create AZAM Pay provider
        provider, _ = models.PaymentProvider.objects.get_or_create(
            name='AZAM Pay',
            defaults={'description': 'AZAM Pay Payment Gateway'}
        )
        
        # Update payment provider if not set
        if not payment.provider:
            payment.provider = provider
            payment.save()
        
        # Get callback URL - use configured webhook URL (production) instead of localhost
        from django.conf import settings
        callback_url = getattr(settings, 'AZAM_PAY_WEBHOOK_URL', None)
        if not callback_url:
            # Fallback to BASE_URL if webhook URL not configured
            base_domain = getattr(settings, 'BASE_URL', 'https://portal.maishaapp.co.tz')
            callback_url = f"{base_domain}/api/v1/payments/webhook/azam-pay/"
        
        # Determine payment method for gateway
        payment_method = 'mobile_money' if payment.payment_method == 'mobile_money' else 'mobile_money'
        
        # Initiate payment with gateway (uses smart phone logic)
        gateway_result = PaymentGatewayService.initiate_payment(
            payment=payment,
            provider_name='azam pay',
            callback_url=callback_url,
            payment_method=payment_method
        )
        
        if not gateway_result['success']:
            error_msg = gateway_result.get('error', 'Failed to initiate payment')
            return Response({
                'success': False,
                'error': 'Payment gateway error',
                'message': f'Unable to initiate payment: {error_msg}. Please try again or contact support if the problem persists.',
                'payment_id': payment.id,
                'details': gateway_result.get('details', {})
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create PaymentTransaction record with the actual payload sent to AZAM Pay
        # This includes accountNumber (phone number) used for the payment
        request_payload = gateway_result.get('request_payload', {})
        if not request_payload:
            # Fallback: create minimal payload if not provided
            request_payload = {'amount': str(payment.amount), 'callback_url': callback_url}
        
        transaction = models.PaymentTransaction.objects.create(
            payment=payment,
            provider=provider,
            azam_reference=gateway_result.get('reference'),
            gateway_transaction_id=gateway_result.get('transaction_id'),
            request_payload=request_payload,  # Store actual payload sent to AZAM Pay (includes phone number)
            response_payload=gateway_result,
            status='initiated'
        )
        
        # Update payment with transaction ID
        payment.transaction_id = gateway_result.get('transaction_id')
        payment.status = 'pending'
        payment.save()
        
        # Extract phone number from request payload for response
        phone_number_used = request_payload.get('accountNumber') if isinstance(request_payload, dict) else None
        
        return Response({
            'success': True,
            'payment_id': payment.id,
            'transaction_id': transaction.id,
            'transaction_reference': gateway_result.get('reference'),
            'gateway_transaction_id': gateway_result.get('transaction_id'),
            'message': gateway_result.get('message', 'Payment initiated successfully. The customer will receive a payment prompt on their phone.'),
            'phone_number_used': phone_number_used,  # Phone number used for payment
            'booking_reference': payment.booking.booking_reference if payment.booking else None,
        }, status=status.HTTP_201_CREATED)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Payment Transaction management
    
    list: Get all payment transactions (filtered by user role)
    retrieve: Get a specific payment transaction
    create: Create a new payment transaction
    update: Update a payment transaction
    partial_update: Partially update a payment transaction
    destroy: Delete a payment transaction
    """
    queryset = models.PaymentTransaction.objects.all()
    serializer_class = serializers.PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
            
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return super().get_queryset()
        # Allow tenant to view transactions for their payments
        return self.queryset.filter(payment__tenant=user)


class PaymentAuditViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Payment Audit logs (Read-only)
    
    list: Get all payment audit logs (filtered by user role)
    retrieve: Get a specific payment audit log
    """
    queryset = models.PaymentAudit.objects.all()
    serializer_class = serializers.PaymentAuditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
            
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return super().get_queryset()
        return self.queryset.filter(payment__tenant=user)


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Expense management
    
    list: Get all expenses (filtered by user role - owners see their properties' expenses)
    retrieve: Get a specific expense
    create: Create a new expense
    update: Update an expense
    partial_update: Partially update an expense
    destroy: Delete an expense
    """
    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
            
        user = self.request.user
        # Only staff/owner can see expenses
        if user.is_staff or user.is_superuser:
            return super().get_queryset()
        # Property owners can see expenses for their properties
        return self.queryset.filter(property__owner=user)


@api_view(['POST'])
@permission_classes([])  # No authentication required for webhooks
@csrf_exempt
def azam_pay_webhook(request):
    """
    Webhook/Callback endpoint for AZAM Pay payment notifications
    
    This endpoint receives payment status updates from AZAM Pay via callback URL.
    According to AzamPay technical support, signature validation is not applicable in this flow.
    
    Flow:
    1. AZAM Pay sends callback after payment completion
    2. Parse callback payload
    3. Update PaymentTransaction status
    4. Update Payment status
    5. Update RentInvoice/Booking if applicable
    
    Note: Signature validation has been removed per AzamPay technical support instructions.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Log incoming webhook for debugging
        logger.info("AzamPay webhook received")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Parse webhook payload
        try:
            raw_body = request.body
            if raw_body:
                payload = json.loads(raw_body.decode('utf-8'))
            else:
                payload = request.data
            logger.info(f"Webhook payload: {payload}")
        except Exception as e:
            logger.warning(f"Failed to parse JSON body, trying request.data: {str(e)}")
            payload = request.data
            if not payload:
                payload = {}
        
        # Parse webhook data
        webhook_data = PaymentGatewayService.parse_webhook_payload(
            payload=payload,
            provider_name='azam pay'
        )
        
        logger.info(f"Parsed webhook data: {webhook_data}")
        
        # Always try direct extraction from payload as fallback/override
        # AzamPay sends: transid, transactionstatus, utilityref, etc.
        if isinstance(payload, dict):
            # Override with direct extraction (more reliable for AzamPay format)
            direct_data = {
                'transaction_id': (
                    payload.get('transid') or  # AzamPay actual field name (PRIORITY)
                    payload.get('transactionId') or
                    payload.get('transaction_id') or
                    payload.get('id') or
                    payload.get('referenceId') or
                    payload.get('reference_id') or
                    payload.get('transId') or
                    webhook_data.get('transaction_id') if webhook_data else None  # Fallback to parsed
                ),
                'reference': (
                    payload.get('reference') or
                    payload.get('externalreference') or  # AzamPay field
                    payload.get('referenceId') or
                    payload.get('ref') or
                    payload.get('reference_id') or
                    webhook_data.get('reference') if webhook_data else None
                ),
                'status': (
                    payload.get('transactionstatus') or  # AzamPay actual field name (PRIORITY)
                    payload.get('status') or
                    payload.get('transaction_status') or
                    webhook_data.get('status') if webhook_data else ''
                ),
                'amount': payload.get('amount') or (webhook_data.get('amount') if webhook_data else None),
                'payment_id': payload.get('payment_id') or payload.get('paymentId') or (webhook_data.get('payment_id') if webhook_data else None),
                'utilityref': payload.get('utilityref'),  # Store for payment lookup
            }
            
            # Merge with parsed data (direct extraction takes priority)
            if webhook_data:
                webhook_data.update(direct_data)
            else:
                webhook_data = direct_data
            
            logger.info(f"After direct extraction: {webhook_data}")
        
        if not webhook_data:
            logger.error(f"Failed to parse webhook payload: {payload}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid webhook payload',
                'message': 'Unable to parse the webhook payload. The payment gateway may have sent data in an unexpected format.',
                'received_payload': str(payload)[:500]  # Limit payload size in response
            }, status=400)
        
        # Get payment from metadata or transaction_id
        payment_id = webhook_data.get('payment_id')
        transaction_id = webhook_data.get('transaction_id')
        utilityref = webhook_data.get('utilityref')  # AzamPay external reference
        
        logger.info(f"Looking for payment - payment_id: {payment_id}, transaction_id: {transaction_id}, utilityref: {utilityref}")
        
        payment = None
        
        if payment_id:
            try:
                payment = models.Payment.objects.get(id=payment_id)
                logger.info(f"Found payment by ID: {payment.id}")
            except models.Payment.DoesNotExist:
                logger.warning(f"Payment with ID {payment_id} not found")
        
        if not payment and transaction_id:
            # Find payment by transaction ID (gateway_transaction_id)
            transaction = models.PaymentTransaction.objects.filter(
                gateway_transaction_id=transaction_id
            ).first()
            if transaction:
                payment = transaction.payment
                logger.info(f"Found payment by transaction ID: {payment.id}")
            else:
                logger.warning(f"Transaction with ID {transaction_id} not found")
        
        # Try to find payment by external reference (utilityref)
        # This matches the externalId used when creating the payment
        # Format: BOOKING-{booking_reference}-{timestamp} or RENT-{payment_id}-{timestamp}
        if not payment and utilityref:
            logger.info(f"Trying to find payment by utilityref: {utilityref}")
            
            if utilityref.startswith('BOOKING-'):
                # Format: BOOKING-HSE-000009-1767956005
                # Extract booking reference (everything after BOOKING- and before last timestamp)
                parts = utilityref.split('-')
                if len(parts) >= 3:
                    # Try different combinations of booking reference
                    # Booking reference could be: HSE-000009 or just the number part
                    booking_ref_variations = [
                        '-'.join(parts[1:-1]),  # HSE-000009 (all middle parts)
                        parts[1] + '-' + parts[2] if len(parts) > 2 else parts[1],  # HSE-000009
                        parts[1],  # Just HSE
                    ]
                    
                    logger.info(f"Trying booking reference variations: {booking_ref_variations}")
                    
                    from properties.models import Booking
                    booking = None
                    for ref_variant in booking_ref_variations:
                        booking = Booking.objects.filter(booking_reference__icontains=ref_variant).first()
                        if booking:
                            logger.info(f"Found booking with reference containing: {ref_variant}")
                            break
                    
                    # Also try exact match with full reference without timestamp
                    if not booking and len(parts) >= 3:
                        booking_ref_full = '-'.join(parts[1:-1])  # Remove BOOKING- prefix and timestamp
                        booking = Booking.objects.filter(booking_reference=booking_ref_full).first()
                        if booking:
                            logger.info(f"Found booking with exact reference: {booking_ref_full}")
                    
                    if booking:
                        # Find the most recent payment linked to this booking
                        payment = models.Payment.objects.filter(booking=booking).order_by('-created_at').first()
                        if payment:
                            logger.info(f"Found payment {payment.id} by booking reference")
                        else:
                            logger.warning(f"Booking found but no payment linked to booking {booking.id}")
            
            elif utilityref.startswith('RENT-'):
                # Format: RENT-{payment_id}-{timestamp}
                # Extract payment ID
                parts = utilityref.split('-')
                if len(parts) >= 2:
                    try:
                        payment_id_from_ref = int(parts[1])
                        payment = models.Payment.objects.filter(id=payment_id_from_ref).first()
                        if payment:
                            logger.info(f"Found payment {payment.id} from RENT utilityref")
                    except (ValueError, IndexError):
                        logger.warning(f"Could not extract payment ID from RENT utilityref: {utilityref}")
            
            # Also try to find by azam_reference if it matches
            if not payment:
                transaction = models.PaymentTransaction.objects.filter(
                    azam_reference=utilityref
                ).first()
                if transaction:
                    payment = transaction.payment
                    logger.info(f"Found payment by azam_reference: {payment.id}")
            
            # Also try finding by reference field in transaction
            if not payment and transaction_id:
                transaction = models.PaymentTransaction.objects.filter(
                    azam_reference=transaction_id
                ).first()
                if transaction:
                    payment = transaction.payment
                    logger.info(f"Found payment by transaction azam_reference: {payment.id}")
        
        if not payment:
            logger.error(f"Could not find payment - payment_id: {payment_id}, transaction_id: {transaction_id}, utilityref: {utilityref}")
            # Return 200 to prevent webhook retries, but log the error
            return JsonResponse({
                'success': False,
                'error': 'Payment or transaction not found',
                'message': f'Could not find payment or transaction with the provided information. Payment ID: {payment_id}, Transaction ID: {transaction_id}',
                'payment_id': payment_id,
                'transaction_id': transaction_id,
                'utilityref': utilityref,
                'payload_keys': list(payload.keys()) if isinstance(payload, dict) else []
            }, status=200)  # Return 200 to prevent retries
        
        # Get or create transaction record
        # Use transaction_id if available, otherwise use reference
        lookup_transaction_id = transaction_id or webhook_data.get('reference')
        
        transaction = None
        if lookup_transaction_id:
            transaction = payment.transactions.filter(
                gateway_transaction_id=lookup_transaction_id
            ).first()
        
        if not transaction:
            # Create new transaction if not found
            provider = models.PaymentProvider.objects.filter(name='AZAM Pay').first()
            if not provider:
                # Create provider if it doesn't exist
                provider = models.PaymentProvider.objects.create(
                    name='AZAM Pay',
                    provider_type='online',
                    is_active=True
                )
            
            transaction = models.PaymentTransaction.objects.create(
                payment=payment,
                provider=provider,
                gateway_transaction_id=lookup_transaction_id or webhook_data.get('reference'),
                azam_reference=webhook_data.get('reference') or lookup_transaction_id,
                request_payload={},
                response_payload=payload,
                status='processing'
            )
            logger.info(f"Created new transaction record: {transaction.id}")
        
        # Update transaction status
        # AzamPay uses 'transactionstatus' field with values like 'success'
        webhook_status = webhook_data.get('status', '').lower()
        if not webhook_status:
            # Try to get from payload directly
            if isinstance(payload, dict):
                webhook_status = payload.get('transactionstatus', '').lower()
        
        logger.info(f"Webhook status: {webhook_status}")
        
        if webhook_status in ['successful', 'success', 'completed', 'success']:
            transaction.status = 'successful'
            payment.status = 'completed'
            payment.paid_date = timezone.now().date()
            logger.info(f"Payment {payment.id} marked as completed")
        elif webhook_status in ['failed', 'failure', 'error', 'fail']:
            transaction.status = 'failed'
            payment.status = 'failed'
            logger.info(f"Payment {payment.id} marked as failed")
        else:
            transaction.status = 'processing'
            logger.info(f"Payment {payment.id} status: processing")
        
        transaction.response_payload = payload
        transaction.gateway_transaction_id = transaction_id or transaction.gateway_transaction_id or webhook_data.get('reference')
        transaction.save()
        payment.save()
        logger.info(f"Transaction {transaction.id} and Payment {payment.id} updated successfully")
        
        # Update rent invoice if this is a rent payment
        if payment.rent_invoice and payment.status == 'completed':
            from django.db.models import Sum
            total_paid = models.Payment.objects.filter(
                rent_invoice=payment.rent_invoice,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            payment.rent_invoice.amount_paid = total_paid
            if payment.rent_invoice.amount_paid >= payment.rent_invoice.total_amount:
                payment.rent_invoice.status = 'paid'
            payment.rent_invoice.save()
        
        # Update booking if this is a booking payment
        if payment.booking and payment.status == 'completed':
            from django.db.models import Sum
            # Calculate total paid from unified payments
            # Note: Payment model uses 'completed' status, not 'successful'
            total_paid = models.Payment.objects.filter(
                booking=payment.booking,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Also include old property payments if they exist
            from properties.models import Payment as PropertyPayment
            old_payments_total = PropertyPayment.objects.filter(
                booking=payment.booking,
                status='active'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            total_paid = total_paid + old_payments_total
            
            payment.booking.paid_amount = total_paid
            payment.booking.update_payment_status()
            payment.booking.save()
        
        # Update visit payment if this is a visit payment
        if payment.status == 'completed':
            from properties.models import PropertyVisitPayment
            visit_payment = PropertyVisitPayment.objects.filter(payment=payment).first()
            if visit_payment:
                visit_payment.status = 'completed'
                visit_payment.paid_at = timezone.now()
                visit_payment.save()
                logger.info(f"Visit payment {visit_payment.id} marked as completed with expiration at {visit_payment.expires_at()}")
        
        return JsonResponse({
            'success': True,
            'payment_id': payment.id,
            'status': payment.status,
            'message': 'Webhook processed successfully'
        })
        
    except Exception as e:
        # Log error but return 200 to prevent webhook retries
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        
        return JsonResponse({
            'success': False,
            'error': 'Webhook processing failed',
            'message': f'An error occurred while processing the webhook: {str(e)}. The payment status may need to be checked manually.',
            'details': str(e)[:200]  # Limit error details length
        }, status=200)  # Return 200 to prevent retries
