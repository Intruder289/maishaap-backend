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
# Swagger documentation - using drf-spectacular (auto-discovery)
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
    create: Create a new payment
    update: Update a payment
    partial_update: Partially update a payment
    destroy: Delete a payment
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

    @swagger_auto_schema(
        method='post',
        operation_description="Initiate a payment transaction for a payment record. Creates a PaymentTransaction and returns transaction details.",
        operation_summary="Initiate Payment Transaction",
        tags=['Payments'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'request_payload': openapi.Schema(type=openapi.TYPE_OBJECT, description='Additional request payload')
            }
        ),
        responses={
            201: serializers.PaymentTransactionSerializer,
            404: "Payment not found",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def initiate(self, request, pk=None):
        """Initiate a payment transaction for a payment record."""
        payment = get_object_or_404(models.Payment, pk=pk)
        # Simulate creating a transaction record and returning a provider redirect
        tx = models.PaymentTransaction.objects.create(
            payment=payment,
            provider=payment.provider,
            request_payload=request.data.get('request_payload', {}),
            status='initiated'
        )
        serializer = serializers.PaymentTransactionSerializer(tx)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
                'error': 'Failed to parse webhook payload',
                'received_payload': payload
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
                'error': 'Payment or transaction not found',
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
            'error': 'Webhook processing failed',
            'message': str(e)
        }, status=200)  # Return 200 to prevent retries
