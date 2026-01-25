from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.dispatch import receiver
from .models import Payment, Booking, Room

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


@receiver(post_save, sender=Booking)
def sync_room_status_on_booking_change(sender, instance, **kwargs):
    """
    Automatically sync room status when booking status changes.
    This ensures rooms become available when bookings are cancelled or checked out.
    """
    # Only process if booking has a room assigned (hotel/lodge bookings)
    if instance.room_number and instance.property_obj:
        try:
            room = Room.objects.get(
                property_obj=instance.property_obj,
                room_number=instance.room_number
            )
            # Sync room status - this will automatically set room to available
            # if no other active bookings exist, or to occupied if there are active bookings
            room.sync_status_from_bookings()
        except Room.DoesNotExist:
            # Room might not exist (e.g., for house bookings), that's okay
            pass


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

