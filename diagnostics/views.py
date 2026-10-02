import random
import uuid
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import DiagnosticCentre, DiagnosticTest, Booking, Payment
from .serializers import (
    UserRegistrationSerializer, 
    DiagnosticCentreSerializer, 
    DiagnosticTestSerializer, 
    BookingSerializer, 
    PaymentSerializer
)
from .tasks import process_payment_webhook_task
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class DiagnosticCentreListView(generics.ListCreateAPIView):
    queryset = DiagnosticCentre.objects.prefetch_related('tests').all()
    serializer_class = DiagnosticCentreSerializer

    # Caching public centre data safely using Redis (Cached for 15 minutes)
    @method_decorator(cache_page(60 * 15, key_prefix='centre_list'))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DiagnosticTestListView(generics.ListCreateAPIView):
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class SimulatedPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        request=inline_serializer(
            name='SimulatedPaymentRequest',
            fields={'booking_id': serializers.IntegerField()}
        ),
        responses={201: PaymentSerializer}
    )

    def post(self, request):
        booking_id = request.data.get('booking_id')
        
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)
        
        if booking.status == 'CONFIRMED':
            return Response({"message": "Booking is already paid and confirmed."}, status=status.HTTP_400_BAD_REQUEST)

        is_success = random.choices([True, False], weights=[80, 20], k=1)[0]
        payment_status = 'SUCCESS' if is_success else 'FAILED'
        
        booking.status = 'CONFIRMED' if is_success else 'FAILED'
        booking.save()

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.amount,
            status=payment_status,
            event_id=f"sim_evt_{uuid.uuid4()}"
        )

        serializer = PaymentSerializer(payment)
        return Response({
            "message": f"Payment processed with status: {payment_status}",
            "payment": serializer.data
        }, status=status.HTTP_201_CREATED)


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=inline_serializer(
            name='PaymentWebhookRequest',
            fields={
                'event_id': serializers.CharField(),
                'booking_id': serializers.IntegerField(),
                'status': serializers.CharField(),
            }
        ),
    )

    def post(self, request):
        event_id = request.data.get('event_id')
        booking_id = request.data.get('booking_id')
        webhook_status = request.data.get('status')

        if not event_id or not booking_id or not webhook_status:
            return Response({"error": "Missing required webhook fields."}, status=status.HTTP_400_BAD_REQUEST)

        if Payment.objects.filter(event_id=event_id).exists():
            return Response({"message": "Event already processed (Idempotent success)."}, status=status.HTTP_200_OK)

        if not Booking.objects.filter(id=booking_id).exists():
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # Offload safely to Celery background task
        process_payment_webhook_task.delay(event_id, booking_id, webhook_status)

        return Response({"message": "Webhook accepted and queued for processing."}, status=status.HTTP_202_ACCEPTED)