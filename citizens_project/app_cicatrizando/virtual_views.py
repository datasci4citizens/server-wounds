import datetime
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request

from .omop.omop_models import ProcedureOccurrence, Provider
from .omop.omop_ids import CID_CONDITION_INACTIVE

from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient, VirtualComorbidity)
from .virtual_serializers import (ImageSerializer, VirtualSpecialistSerializer, VirtualWoundSerializer, VirtualTrackingRecordsSerializer, 
                                 VirtualPatientSerializer, VirtualComorbiditySerializer, ImageSerializer)
from django.db.models import OuterRef, Subquery
from .models import TrackingRecordImage, WoundImage, User, PatientNonClinicalInfos
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
from rest_framework.exceptions import APIException

class ForbiddenException(APIException):
    status_code = 403
    default_detail = 'Usuario nao autorizado.'

class UserAuth:
    user : User
    def __init__(self, user):
        self.user =  user
        self.patient_info = None
        self.provider = None
    def load_specialist(self, raise_exception=True):
        try: 
            self.provider  = Provider.objects.get(provider_user_id=self.user.id)
        except Provider.DoesNotExist:
            if raise_exception:
                return ForbiddenException(detail="Usuario deve ser um especialista.")
    def load_patient(self, raise_exception=True):
        try: 
            self.patient_info  = PatientNonClinicalInfos.objects.get(user_id=self.user.id)
        except PatientNonClinicalInfos.DoesNotExist:
            if raise_exception:
                return ForbiddenException(detail="Usuario deve ser um paciente.")
    
    def specialist_id_is(self, id):
        if int(id) != self.provider.provider_id:
            raise  ForbiddenException(detail="O especialista nao tem permissao de acesso a esse endpoint") 
    def or_specialist_id_is(self, id):
        if self.provider != None:
            self.specialist_id_is(id) 
        
    def patient_id_is(self, id):
        if int(id) != self.patient_info.person_id:
            raise  ForbiddenException(detail="O paciente nao tem permissao de acessar esse endpoint.") 
    def or_patient_id_is(self, id):
        if self.patient_info != None:
            self.patient_id_is(id) 

@extend_schema(tags=["patients"])
class VirtualPatientViewSet(viewsets.ViewSet):
    queryset  = VirtualPatient.objects().all()
    serializer_class = VirtualPatientSerializer
    def create(self, request, *args, **kwargs):
        serializer = VirtualPatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth = UserAuth(request.user)
        auth.load_specialist()
        auth.specialist_id_is(serializer.validated_data["specialist_id"])
        data = serializer.create(serializer.validated_data)         
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        auth = UserAuth(request.user)
        auth.load_patient(raise_exception=False)
        auth.or_patient_id_is(int(pk))
        auth.load_specialist(raise_exception=False)

        instance = VirtualPatient.get(patient_id=pk)
        auth.or_specialist_id_is(instance["specialist_id"])
        comorbidities = VirtualPatient.get_comorbidities(patient_id=pk)
        instance["comorbidities"] = comorbidities
        return Response(instance)


    def list(self, request, *args, **kwargs):
        specialist_id = self.request.query_params.get('specialist_id')
        instances = VirtualPatient.objects().all()
        auth = UserAuth(request.user)
        auth.load_specialist()
        if specialist_id != None and specialist_id != "":
            auth.specialist_id_is(specialist_id)
            instances = instances.filter(specialist_id=int(specialist_id))
        else:
            raise ForbiddenException(detail="Se deve usar o query param filtrando pelo especialista, /patients?specialist_id={specialist_id}")
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
    
    def create(self, request, *args, **kwargs):
        serializer = VirtualWoundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data;
        data["updated_at"] = datetime.datetime.now()
        
        # Criar a ferida no banco usando o modelo virtual
        instance = VirtualWound.create(data)
        
        # Se uma imagem foi enviada, criar o registro de imagem
        if 'image' in request.FILES:
            image_serializer = ImageSerializer(data={'image': request.FILES['image']})
            if image_serializer.is_valid():
                image = image_serializer.save()
                WoundImage.objects.create(
                    wound_id=instance['wound_id'],
                    image=image
                )
        
        return Response(instance, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.queryset.get(wound_id=pk)
        if instance.get("image_url"):
            instance["image_url"] = request.build_absolute_uri("../" + "media/" + instance.get("image_url"))
        instance.pop("image_id")

        serializer = VirtualWoundSerializer(data=instance)
        serializer.is_valid(raise_exception=True)
        return Response(instance)

    def list(self, request: Request, *args, **kwargs):
        instances = list(self.queryset.all())
        for instance in instances:            
            if instance.get("image_url"):
                instance["image_url"] = request.build_absolute_uri("../" + "media/" + instance.get("image_url"))
            instance.pop("image_id")
        serializer = VirtualWoundSerializer(many=True, data=instances)
        serializer.is_valid(raise_exception=True)
        return Response(instances)
      
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
            # 3. Prepara os dados para atualização no modelo VirtualWound
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

    @action(detail=True, methods=['put'], url_path='archive', serializer_class=None)
    def archive(self, request, pk=None):
        instance = VirtualWound.get(wound_id=pk)
        if not instance:
            return Response({'error': 'Wound not found'}, status=status.HTTP_404_NOT_FOUND)
            
        # Marcar a ferida como inativa usando o Concept ID apropriado
        instance["is_active"] = False
        updated_instance = VirtualWound.update(data=instance)
        
        return Response(updated_instance)
    
@extend_schema(tags=["tracking-records"])
class VirtualTrackingRecordsViewSet(viewsets.ModelViewSet):
    queryset = VirtualTrackingRecords.objects().all().annotate(
        image_url=Subquery(
            TrackingRecordImage.objects.filter(tracking_record_id=OuterRef('tracking_id')).values('image__image')
        )
    )
    serializer_class = VirtualTrackingRecordsSerializer
    def create(self, request, *args, **kwargs):
        serializer = VirtualTrackingRecordsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data_to_create = serializer.validated_data
        data_to_create["track_date"] = datetime.date.today()
        if(data_to_create.get("extra_notes", None) == None):
            data_to_create["extra_notes"] = ""
        if(data_to_create.get("guidelines_to_patient", None) == None):
            data_to_create["guidelines_to_patient"] = ""
        data = VirtualTrackingRecords.create(data_to_create)
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.queryset.get(tracking_id=pk)
        instance["image_url"] = request.build_absolute_uri("../" +"media/"+ instance.get("image_url"))
        instance.pop("image_id")
        return Response(instance)


    def list(self, request: Request, *args, **kwargs):
        instances = list(self.queryset.all())
        for instance in instances:
            if instance.get("image_url", None) != None:
                instance["image_url"] = request.build_absolute_uri("../" +"media/"+ instance.get("image_url"))
            instance.pop("image_id")
        return Response(instances)
    
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
