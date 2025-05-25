from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from app_cicatrizando.api import GoogleLoginView, MeView
from . import virtual_views
from . import views
from .omop_views import router as omop_router

# from django_scalar.views import scalar_viewer
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from app_cicatrizando.scalar import scalar_viewer

from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, SpecialistViewSet, WoundViewSet,
    TrackingRecordViewSet, ComorbidityViewSet, ImageViewSet,WoundExcelView
)

# --- ROUTER ---

router = DefaultRouter()
router.register(r'specialists', SpecialistViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'comorbidities', ComorbidityViewSet)
router.register(r'images', ImageViewSet)
router.register(r'wounds', WoundViewSet)
router.register(r'tracking-records', TrackingRecordViewSet)
router.register(r'auth/login/google', GoogleLoginView, basename='google-login')
router.register(r'auth/me', MeView, basename='me')
# --- URLS ---

urlpatterns = [
    path('', include(router.urls)),
    path('', include(omop_router.urls)),
    path('virtual-', include(virtual_views.router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/swagger", SpectacularSwaggerView.as_view(), name="schema-swagger-ui"),
    path("docs", scalar_viewer, name="schema-scalar-ui"), 
    path('api/wounds/excel/', WoundExcelView.as_view(), name='wounds-excel'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)