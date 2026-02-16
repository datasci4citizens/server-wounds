from django.urls import path, include
from rest_framework import routers
from .api import GoogleLoginView, MeView
from drf_spectacular.views import SpectacularSwaggerView

router = routers.DefaultRouter()

# Auth endpoints
router.register(r'auth/login/google', GoogleLoginView, basename='google-login')
router.register(r'auth/me', MeView, basename='me')

urlpatterns = [
    path('', include(router.urls)),
    
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
