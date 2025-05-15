from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

# from django_scalar.views import scalar_viewer
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from app_cicatrizando.scalar import scalar_viewer

from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, SpecialistViewSet, WoundViewSet,
    TrackingRecordViewSet, ComorbidityViewSet, ImageViewSet,WoundExcelView
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'specialists', SpecialistViewSet)
router.register(r'wounds', WoundViewSet)
router.register(r'tracking-records', TrackingRecordViewSet)
router.register(r'comorbidities', ComorbidityViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger", SpectacularSwaggerView.as_view(), name="schema-swagger-ui"),
    path("api/schema/scalar", scalar_viewer, name="schema-scalar-ui"), 
    path('api/wounds/excel/', WoundExcelView.as_view(), name='wounds-excel'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)