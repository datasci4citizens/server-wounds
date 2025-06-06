from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient, VirtualComorbidity)
from .virtual_serializers import (VirtualSpecialistSerializer, VirtualWoundSerializer, VirtualTrackingRecordsSerializer, 
                                 VirtualPatientSerializer, VirtualComorbiditySerializer)
from rest_framework.response import Response

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

@extend_schema(tags=["comorbidities"])
class VirtualComorbidityViewSet(viewsets.ModelViewSet):
    queryset = VirtualComorbidity.objects().all()
    serializer_class = VirtualComorbiditySerializer
    
    def get_queryset(self):
        queryset = VirtualComorbidity.objects().all()
        patient_id = self.request.query_params.get('patient_id', None)
        if patient_id is not None:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset
        
    def create(self, request, *args, **kwargs):
        """
        Método personalizado para criar comorbidades garantindo que o conceito exista
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Já validamos o comorbidity_type no serializer
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
