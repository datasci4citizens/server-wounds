from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient)
from .virtual_serializers import (VirtualSpecialistSerializer, VirtualWoundSerializer, VirtualTrackingRecordsSerializer, VirtualPatientSerializer)


@extend_schema(tags=["specialists"])
class VirtualSpecialistViewSet(viewsets.ModelViewSet):
    queryset  = VirtualSpecialist.objects().all()
    serializer_class = VirtualSpecialistSerializer

@extend_schema(tags=["patients"])
class VirtualPatientViewSet(viewsets.ModelViewSet):
    queryset  = VirtualPatient.objects().all()
    serializer_class = VirtualPatientSerializer

@extend_schema(tags=["wounds"])
class VirtualWoundViewSet(viewsets.ModelViewSet):
    queryset = VirtualWound.objects().all()
    serializer_class = VirtualWoundSerializer

@extend_schema(tags=["tracking-records"])
class VirtualTrackingRecordsViewSet(viewsets.ModelViewSet):
    queryset = VirtualTrackingRecords.objects().all()
    serializer_class = VirtualTrackingRecordsSerializer
