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
    
    # Método `update` implementado na View

    def update(self, request, pk=None, *args, **kwargs):
        # 1. Obtém a instância existente da ferida
        instance = VirtualWound.get(wound_id=pk)
        if not instance:
            return Response({'error': 'Wound not found'}, status=status.HTTP_404_NOT_FOUND)

        # 2. Instancia o serializer com os dados existentes e os dados da requisição
        #    `partial=kwargs.get('partial', False)` permite que o mesmo método `update`
        #    lida com PUT (false) e PATCH (true) automaticamente.
        serializer = self.get_serializer(instance=instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # 3. Prepara os dados para a atualização no modelo VirtualWound
            update_data = {
                "wound_id": instance["wound_id"], 
                "updated_at": datetime.now() 
            }

            # Copia apenas os campos válidos e atualizáveis do serializer para update_data
            for field_name in [
                "patient_id", "specialist_id", "region", "wound_type",
                "start_date", "end_date", "is_active"
            ]:
                if field_name in serializer.validated_data:
                    update_data[field_name] = serializer.validated_data[field_name]
                # Se for PATCH e o campo não estiver em validated_data, seu valor será mantido

            # 4. Chama o método .update() do seu VirtualWound para persistir as mudanças no OMOP
            updated_instance_data = VirtualWound.update(update_data)

            # 5. Lida com a atualização da imagem, se um novo arquivo for enviado
            if 'image' in request.FILES:
                image_serializer = ImageSerializer(data={'image': request.FILES['image']})
                if image_serializer.is_valid(raise_exception=True):
                    new_image = image_serializer.save() # Salva a nova imagem no sistema de arquivos/DB

                    # Tenta encontrar e atualizar o registro WoundImage existente
                    try:
                        wound_image_record = WoundImage.objects.get(wound_id=updated_instance_data['wound_id'])
                        wound_image_record.image = new_image
                        wound_image_record.save()
                    except WoundImage.DoesNotExist:
                        # Se não havia um registro de imagem associado, cria um novo
                        WoundImage.objects.create(
                            wound_id=updated_instance_data['wound_id'],
                            image=new_image
                        )

        return Response(updated_instance_data)
   
    
    #----------------------------------------------------------------------------------------

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
        except TrackingRecordImage.DoesNotExist:
            return Response({"error": "Tracking record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Image updated successfully"}, status=status.HTTP_200_OK)

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
            
        except WoundImage.DoesNotExist:
            return Response({"error": "Tracking record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Image updated successfully"}, status=status.HTTP_200_OK)

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
