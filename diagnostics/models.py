from django.db import models
from django.contrib.auth.models import User
import uuid

class DiagnosticCentre(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.name} - {self.location}"

class DiagnosticTest(models.Model):
    centre = models.ForeignKey(DiagnosticCentre, related_name='tests', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.centre.name}) - ${self.price}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    test = models.ForeignKey(DiagnosticTest, on_delete=models.CASCADE)
    centre = models.ForeignKey(DiagnosticCentre, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} ({self.status})"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    event_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # For webhook idempotency
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"