from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from app_cicatrizando.api import GoogleLoginView, MeView
from . import virtual_urls
from .omop.omop_views import router as omop_router

# from django_scalar.views import scalar_viewer
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from app_cicatrizando.scalar import scalar_viewer

from rest_framework.routers import DefaultRouter

# --- ROUTER ---

router = DefaultRouter() 
router.register(r'auth/login/google', GoogleLoginView, basename='google-login')
router.register(r'auth/me', MeView, basename='me')
# --- URLS ---

urlpatterns = [
    path('', include(router.urls)),
    path('omop/', include(omop_router.urls)),
    path('', include(virtual_urls.router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/redoc", SpectacularRedocView.as_view(), name="redoc"),
    path("docs/swagger", SpectacularSwaggerView.as_view(), name="schema-swagger-ui"),
    path("docs", scalar_viewer, name="schema-scalar-ui"), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)