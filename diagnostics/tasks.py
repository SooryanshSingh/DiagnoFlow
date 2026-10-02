from celery import shared_task
from django.db import transaction
from .models import Booking, Payment

@shared_task(
    bind=True, 
    max_retries=3,              
    default_retry_delay=10,      # Wait 10 seconds before the first retry
    autoretry_for=(Exception,), 
    retry_backoff=True           # Exponentially increase delay between retries
)
def process_payment_webhook_task(self, event_id, booking_id, status):
    if Payment.objects.filter(event_id=event_id).exists():
        return f"Event {event_id} already processed (Idempotent safe-exit)."

    try:
        with transaction.atomic():
            booking = Booking.objects.get(id=booking_id)

            Payment.objects.create(
                booking=booking,
                event_id=event_id,
                status=status,
                amount=booking.amount
            )

            booking.status = 'CONFIRMED' if status == 'SUCCESS' else 'FAILED'
            booking.save()

            return f"Webhook successfully processed for booking {booking_id}"
            
    except Exception as exc:
        raise self.retry(exc=exc)