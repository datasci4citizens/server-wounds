from rest_framework.routers import DefaultRouter
from .virtual_views import(VirtualPatientViewSet, VirtualSpecialistViewSet, VirtualWoundViewSet, 
                         VirtualTrackingRecordsViewSet, VirtualComorbidityViewSet)

router = DefaultRouter()
router.register(r'patients', VirtualPatientViewSet)
router.register(r'specialists', VirtualSpecialistViewSet)
router.register(r'wounds', VirtualWoundViewSet)
router.register(r'tracking-records', VirtualTrackingRecordsViewSet)
router.register(r'comorbidities', VirtualComorbidityViewSet)