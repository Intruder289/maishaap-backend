from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.dispatch import receiver
from .models import Payment, Booking

try:
    from documents.models import Booking as DocumentBooking, Lease
except Exception:
    DocumentBooking = None
    Lease = None


@receiver(post_save, sender=Payment)
def update_booking_payment_status(sender, instance, created, **kwargs):
    """
    Update booking payment status when payment is saved.
    This ensures expired bookings are checked after payment is recorded.
    """
    if instance.status == 'active':  # Only process active payments
        booking = instance.booking
        # Recalculate paid amount
        total_paid = booking.booking_payments.filter(status='active').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        booking.paid_amount = total_paid
        booking.update_payment_status()
        
        # Note: We don't need to check expiration here because:
        # 1. If payment is made, booking is no longer expired
        # 2. The management command will handle expired bookings
        # 3. Checking here could cause issues if payment is being saved during booking creation
        return


if DocumentBooking:
    @receiver(post_save, sender=DocumentBooking)
    def sync_property_status_from_document_booking(sender, instance, **kwargs):
        instance.property_ref.refresh_status_from_activity()

    @receiver(post_delete, sender=DocumentBooking)
    def sync_property_status_from_document_booking_delete(sender, instance, **kwargs):
        instance.property_ref.refresh_status_from_activity()


if Lease:
    @receiver(post_save, sender=Lease)
    def sync_property_status_from_lease(sender, instance, **kwargs):
        instance.property_ref.refresh_status_from_activity()

    @receiver(post_delete, sender=Lease)
    def sync_property_status_from_lease_delete(sender, instance, **kwargs):
        instance.property_ref.refresh_status_from_activity()

