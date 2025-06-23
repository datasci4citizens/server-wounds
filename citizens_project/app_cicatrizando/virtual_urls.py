from rest_framework.routers import DefaultRouter
from .virtual_views import(VirtualPatientViewSet, VirtualSpecialistViewSet, VirtualWoundViewSet, 
                         VirtualTrackingRecordsViewSet, VirtualComorbidityViewSet, TrackingRecordsImageViewSet, WoundImageViewSet, ImageViewSet)

router = DefaultRouter()
router.register(r'patients', VirtualPatientViewSet)
router.register(r'specialists', VirtualSpecialistViewSet)
router.register(r'images', ImageViewSet)
router.register(r'wounds', VirtualWoundViewSet)
router.register(r'wounds/image', WoundImageViewSet, basename='wounds-image')
router.register(r'tracking-records', VirtualTrackingRecordsViewSet)
router.register(r'tracking-records/image', TrackingRecordsImageViewSet, basename='tracking-records-image')
router.register(r'comorbidities', VirtualComorbidityViewSet)