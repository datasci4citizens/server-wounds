from django.urls import path, include
from rest_framework import routers
from .views import GoogleLoginView, RoleSelectionView, ProviderProfileView, PatientProfileView, MeView
from drf_spectacular.views import SpectacularSwaggerView

router = routers.DefaultRouter()

# Auth endpoints
router.register(r'auth/login/google', GoogleLoginView, basename='google-login')
router.register(r'auth/login/role', RoleSelectionView, basename='role-selection')
router.register(r'auth/login/provider', ProviderProfileView, basename='provider-profile')
router.register(r'auth/login/patient', PatientProfileView, basename='patient-profile')
router.register(r'auth/me', MeView, basename='me')

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
