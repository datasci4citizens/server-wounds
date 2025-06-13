from django.conf import settings
from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request

from .omop.omop_models import ProcedureOccurrence

from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient, VirtualComorbidity)
from .virtual_serializers import (ImageSerializer, VirtualSpecialistSerializer, VirtualWoundSerializer, VirtualTrackingRecordsSerializer, 
                                 VirtualPatientSerializer, VirtualComorbiditySerializer, ImageSerializer)
from django.db.models import OuterRef, Subquery
from .models import TrackingRecordImage, WoundImage, User
from rest_framework import generics, mixins, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .predict_single_image import predict_image_class, predict_multi_label
from PIL import Image

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
        data = serializer.create(serializer.validated_data)
        VirtualPatient._map_virtual_to_db
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = VirtualPatient.get(patient_id=pk)
        comorbidities = VirtualPatient.get_comorbidities(patient_id=pk)
        instance["comorbidities"] = comorbidities
        serializer = VirtualPatientSerializer()
        return Response(instance)


    def list(self, request, *args, **kwargs):
        instances = VirtualPatient.objects().all()
        for instance in instances:
            comorbidities = VirtualPatient.get_comorbidities(patient_id=instance["patient_id"])
            instance["comorbidities"] = comorbidities
        return Response(instances)
    
    
@extend_schema(tags=["wounds"])
class VirtualWoundViewSet(viewsets.ModelViewSet):
    queryset = VirtualWound.objects().annotate(
        image_url=Subquery(
            WoundImage.objects.filter(wound_id=OuterRef('wound_id')).values('image__image')
        )
    ).all()
    serializer_class = VirtualWoundSerializer
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.queryset.get(tracking_id=pk)
        instance["image_url"] = request.build_absolute_uri("../" +"media/"+ instance.get("image_url"))
        serializer = VirtualWoundSerializer(data=instance)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)

    def list(self, request: Request, *args, **kwargs):
        instances = list(self.queryset.all())
        for instance in instances:            
            instance["image_url"] = request.build_absolute_uri("../" +"media/"+ instance.get("image_url"))
        serializer =  VirtualWoundSerializer(many=True, data=instances)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
@extend_schema(tags=["tracking-records"])
class VirtualTrackingRecordsViewSet(viewsets.ModelViewSet):
    queryset = VirtualTrackingRecords.objects().all().annotate(
        image_url=Subquery(
            TrackingRecordImage.objects.filter(tracking_record_id=OuterRef('tracking_id')).values('image__image')
        )
    )
    serializer_class = VirtualTrackingRecordsSerializer
    def create(self, request, *args, **kwargs):
        serializer = VirtualPatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.create(serializer.validated_data)
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.queryset.get(tracking_id=pk)
        instance["image_url"] = request.build_absolute_uri("../" +"media/"+ instance.get("image_url"))
        serializer = VirtualTrackingRecordsSerializer(data=instance)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)


    def list(self, request: Request, *args, **kwargs):
        instances = list(self.queryset.all())
        for instance in instances:            
            instance["image_url"] = request.build_absolute_uri("../" +"media/"+ instance.get("image_url"))
        serializer =  VirtualTrackingRecordsSerializer(many=True, data=instances)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
    
@extend_schema(tags=["tracking-records"])
class TrackingRecordsImageViewSet(viewsets.ViewSet):
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser]
    def update(self, request,pk, *args, **kwargs):
        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try: 
            tracking_image_instance = TrackingRecordImage.objects.get(tracking_record_id=pk)
            image_instance = serializer.save()
            tracking_image_instance.image = image_instance
            tracking_image_instance.save()

            uploaded_image = request.FILES.get("image")
            if uploaded_image is None:
                return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

            pil_image = Image.open(uploaded_image).convert("RGB")

            tissue_prediction = predict_image_class(pil_image)
            multihead_predictions = predict_multi_label(pil_image)

        except TrackingRecordImage.DoesNotExist:
            return Response({"error": "Tracking record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
                "message": "Image updated successfully",
                "predictions": {
                    "tissue_type": tissue_prediction,
                    "W_I_Fi": multihead_predictions
                }
            }, status=status.HTTP_200_OK)

@extend_schema(tags=["wounds"])
class WoundImageViewSet(viewsets.ViewSet):
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser]

    def update(self, request,pk, *args, **kwargs):
        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try: 
            wound_image_instance = WoundImage.objects.get(wound_id=pk)
            image_instance = serializer.save()
            wound_image_instance.image = image_instance
            wound_image_instance.save()

            uploaded_image = request.FILES.get('image')
            if uploaded_image is None:
                return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            pil_image = Image.open(uploaded_image).convert("RGB")

            tissue_prediction = predict_image_class(pil_image)
            multihead_predictions = predict_multi_label(pil_image)
            

        except WoundImage.DoesNotExist:
            return Response({"error": "Tracking record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
                "message": "Image updated successfully",
                "predictions": {
                    "tissue_type": tissue_prediction,
                    "W_I_Fi": multihead_predictions
                }
            }, status=status.HTTP_200_OK)

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
