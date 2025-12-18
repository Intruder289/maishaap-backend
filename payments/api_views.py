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
import json


class PaymentProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.PaymentProvider.objects.all()
    serializer_class = serializers.PaymentProviderSerializer
    permission_classes = [permissions.IsAuthenticated]


class InvoiceViewSet(viewsets.ModelViewSet):
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
    Webhook endpoint for AZAM Pay payment notifications
    
    This endpoint receives payment status updates from AZAM Pay.
    It verifies the webhook signature and updates payment records.
    
    Flow:
    1. AZAM Pay sends webhook after payment completion
    2. Verify webhook signature
    3. Parse webhook payload
    4. Update PaymentTransaction status
    5. Update Payment status
    6. Update RentInvoice if applicable
    """
    try:
        # Get raw body for signature verification
        raw_body = request.body
        
        # Get signature from headers
        # AZAM Pay typically sends signature in X-Signature or X-Azam-Pay-Signature header
        signature = (
            request.headers.get('X-Signature') or
            request.headers.get('X-Azam-Pay-Signature') or
            request.headers.get('X-Webhook-Signature') or
            request.headers.get('Authorization')
        )
        
        # Verify webhook signature
        if not PaymentGatewayService.verify_webhook_signature(
            payload=raw_body,
            signature=signature,
            provider_name='azam pay'
        ):
            return JsonResponse({
                'error': 'Invalid webhook signature'
            }, status=400)
        
        # Parse webhook payload
        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except:
            payload = request.data
        
        # Parse webhook data
        webhook_data = PaymentGatewayService.parse_webhook_payload(
            payload=payload,
            provider_name='azam pay'
        )
        
        if not webhook_data:
            return JsonResponse({
                'error': 'Failed to parse webhook payload'
            }, status=400)
        
        # Get payment from metadata or transaction_id
        payment_id = webhook_data.get('payment_id')
        transaction_id = webhook_data.get('transaction_id')
        
        if payment_id:
            payment = get_object_or_404(models.Payment, id=payment_id)
        elif transaction_id:
            # Find payment by transaction ID
            transaction = models.PaymentTransaction.objects.filter(
                gateway_transaction_id=transaction_id
            ).first()
            if not transaction:
                return JsonResponse({
                    'error': 'Transaction not found'
                }, status=404)
            payment = transaction.payment
        else:
            return JsonResponse({
                'error': 'Payment ID or transaction ID required'
            }, status=400)
        
        # Get or create transaction record
        transaction = payment.transactions.filter(
            gateway_transaction_id=transaction_id
        ).first()
        
        if not transaction:
            # Create new transaction if not found
            provider = models.PaymentProvider.objects.filter(name='AZAM Pay').first()
            transaction = models.PaymentTransaction.objects.create(
                payment=payment,
                provider=provider,
                gateway_transaction_id=transaction_id,
                azam_reference=webhook_data.get('reference'),
                request_payload={},
                response_payload=payload,
                status='processing'
            )
        
        # Update transaction status
        webhook_status = webhook_data.get('status', '').lower()
        if webhook_status in ['successful', 'success', 'completed']:
            transaction.status = 'successful'
            payment.status = 'completed'
            payment.paid_date = timezone.now().date()
        elif webhook_status in ['failed', 'failure', 'error']:
            transaction.status = 'failed'
            payment.status = 'failed'
        else:
            transaction.status = 'processing'
        
        transaction.response_payload = payload
        transaction.save()
        payment.save()
        
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
