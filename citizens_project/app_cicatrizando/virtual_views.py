from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema
from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient)
from .virtual_serializers import (VirtualSpecialistSerializer, VirtualWoundSerializer, VirtualTrackingRecordsSerializer, VirtualPatientSerializer)
from django.db.models import OuterRef, Subquery
from .models import User 
from rest_framework import generics, mixins, views
from rest_framework.response import Response

@extend_schema(tags=["specialists"])
class VirtualSpecialistViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset  = VirtualSpecialist.objects().annotate(
		email = Subquery(User.objects.all().filter(id=OuterRef("user_id")).values("email")[:1])
	)
    serializer_class = VirtualSpecialistSerializer

@extend_schema(tags=["patients"])
class VirtualPatientViewSet(viewsets.ViewSet):
    queryset  = VirtualPatient.objects().all()
    serializer_class = VirtualPatientSerializer

    def create(self, request, *args, **kwargs):
        
        serializer = VirtualPatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(tags=["wounds"])
class VirtualWoundViewSet(viewsets.ModelViewSet):
    queryset = VirtualWound.objects().all()
    serializer_class = VirtualWoundSerializer

@extend_schema(tags=["tracking-records"])
class VirtualTrackingRecordsViewSet(viewsets.ModelViewSet):
    queryset = VirtualTrackingRecords.objects().all()
    serializer_class = VirtualTrackingRecordsSerializer
