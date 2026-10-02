from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.openapi import AutoSchema

# Explicitly force drf-spectacular's AutoSchema onto the SimpleJWT views
TokenObtainPairView.schema = AutoSchema()
TokenRefreshView.schema = AutoSchema()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('diagnostics.urls')),
    
    # Direct Standard JWT Auth Endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # OpenAPI 3 Documentation routes
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]