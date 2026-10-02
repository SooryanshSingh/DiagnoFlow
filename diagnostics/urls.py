from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegisterView, 
    DiagnosticCentreListView, 
    DiagnosticTestListView, 
    BookingListCreateView, 
    SimulatedPaymentView, 
    PaymentWebhookView
)

urlpatterns = [
    # Auth Endpoints
    path('auth/signup/', UserRegisterView.as_view(), name='signup'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Centre & Test Endpoints
    path('centres/', DiagnosticCentreListView.as_view(), name='centre-list'),
    path('tests/', DiagnosticTestListView.as_view(), name='test-list'),
    
    # Bookings & Payments
    path('bookings/', BookingListCreateView.as_view(), name='booking-list-create'),
    path('payments/', SimulatedPaymentView.as_view(), name='simulated-payment'),
    path('payments/webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
]