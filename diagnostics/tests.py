from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import DiagnosticCentre, DiagnosticTest, Booking, Payment

class DiagnosticBookingAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='securepassword123')
        
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'securepassword123'
        }, format='json')
        self.token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.centre = DiagnosticCentre.objects.create(name='City Lab', location='Downtown')
        self.diagnostic_test = DiagnosticTest.objects.create(
            centre=self.centre,
            name='Blood Panel',
            description='Full blood work',
            price=150.00
        )

    def test_get_diagnostic_centres(self):
        """Test public retrieval of diagnostic centres and nested tests."""
        self.client.credentials() 
        response = self.client.get('/api/centres/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'City Lab')

    def test_create_booking_authenticated(self):
        """Test that an authenticated user can successfully create a booking."""
        payload = {
            "test": self.diagnostic_test.id,
            "centre": self.centre.id,
            "appointment_datetime": "2026-06-01T10:00:00Z"
        }
        response = self.client.post('/api/bookings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(float(response.data['amount']), 150.00)

    def test_webhook_idempotency(self):
        """Test that sending the same webhook event ID twice behaves idempotently."""
        booking = Booking.objects.create(
            user=self.user,
            test=self.diagnostic_test,
            centre=self.centre,
            appointment_datetime="2026-06-01T10:00:00Z",
            amount=150.00,
            status='PENDING'
        )

        webhook_payload = {
            "event_id": "evt_test_unique_123",
            "booking_id": booking.id,
            "status": "SUCCESS"
        }

        response1 = self.client.post('/api/payments/webhook/', webhook_payload, format='json')
        self.assertIn(response1.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED])

        response2 = self.client.post('/api/payments/webhook/', webhook_payload, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertIn("already processed", response2.data['message'])

        payment_count = Payment.objects.filter(event_id="evt_test_unique_123").count()
        self.assertEqual(payment_count, 1)