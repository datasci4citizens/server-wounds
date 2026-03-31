from django.urls import path, include
from rest_framework import routers
from .views import GoogleLoginView, SpecialistRegistrationView, MeView
from drf_spectacular.views import SpectacularSwaggerView

router = routers.DefaultRouter()

# Auth endpoints
router.register(r'auth/google', GoogleLoginView, basename='google-login')
router.register(r'auth/register/specialist', SpecialistRegistrationView, basename='specialist-registration')
router.register(r'auth/me', MeView, basename='me')

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
