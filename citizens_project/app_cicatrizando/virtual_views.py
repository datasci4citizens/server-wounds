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
from .models import Image, TrackingRecordImage, WoundImage, User, PatientNonClinicalInfos
from rest_framework import generics, mixins, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.db import transaction

#from .wound_pixel_counter import count_pixels_simple
from .predict_single_image import predict_image_class, predict_multi_label
from PIL import Image as PILImage
#from .identifica_ref import get_reference_area

from rest_framework.exceptions import APIException


@extend_schema(tags=["images"])
class ImageViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    # Define o queryset para todas as imagens.
    queryset = Image.objects.all()
    # Define o serializer a ser usado para a serialização/deserialização de imagens.
    serializer_class = ImageSerializer
    # Define os parsers de requisição, permitindo o upload de arquivos (multipart/form-data).
    parser_classes = [MultiPartParser]

@extend_schema(tags=["specialists"])
class VirtualSpecialistViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    # Define o queryset para buscar especialistas, adicionando o email do usuário associado.
    queryset  = VirtualSpecialist.objects().annotate(
        email = Subquery(User.objects.all().filter(id=OuterRef("user_id")).values("email")[:1])
    )
    # Define o serializer para especialistas virtuais.
    serializer_class = VirtualSpecialistSerializer

class ForbiddenException(APIException):
    # Define o código de status HTTP para a exceção.
    status_code = 403
    # Define a mensagem de detalhe padrão para a exceção.
    default_detail = 'Usuario nao autorizado.'


class ConflictException(APIException):
    # Define o código de status HTTP para a exceção de conflito.
    status_code = status.HTTP_409_CONFLICT

class UserAuth:
    # Atributo para armazenar o objeto User.
    user : User
    def __init__(self, user):
        # Inicializa a classe com o usuário logado.
        self.user =  user
        # Atributos para armazenar informações de paciente e provedor (especialista).
        self.patient_info = None
        self.provider = None
    def load_specialist(self, raise_exception=True):
        # Tenta carregar as informações do especialista associado ao usuário.
        try: 
            self.provider  = Provider.objects.get(provider_user_id=self.user.id)
        except Provider.DoesNotExist:
            # Se o especialista não for encontrado e raise_exception for True, levanta uma ForbiddenException.
            if raise_exception:
                raise ForbiddenException(detail="Usuario deve ser um especialista.")
    def load_patient(self, raise_exception=True):
        # Tenta carregar as informações do paciente associado ao usuário.
        try: 
            self.patient_info  = PatientNonClinicalInfos.objects.get(user_id=self.user.id)
        except PatientNonClinicalInfos.DoesNotExist:
            # Se o paciente não for encontrado e raise_exception for True, levanta uma ForbiddenException.
            if raise_exception:
                raise ForbiddenException(detail="Usuario deve ser um paciente.")
    
    def specialist_id_is(self, id, detail="O especialista nao tem permissao de acesso a este recurso com estes parametros especificos (pode estar faltando ou tendo parametros errados)"):
        # Verifica se o provedor foi carregado, caso contrário, tenta carregá-lo.
        if self.provider == None:
            self.load_specialist()
        # Compara o ID fornecido com o ID do provedor. Se forem diferentes, levanta uma ForbiddenException.
        if int(id) != self.provider.provider_id:
            raise  ForbiddenException(detail=detail) 
    def if_specialist_id_is(self, id, detail="O especialista nao tem permissao de acesso a este recurso com estes parametros especificos (pode estar faltando ou tendo parametros errados)"):
        # Tenta carregar o especialista, mas não levanta exceção se não encontrar.
        if self.provider == None:
            self.load_specialist(raise_exception=None)
        # Se o provedor for encontrado, chama specialist_id_is para verificar a permissão.
        if self.provider != None:
            self.specialist_id_is(id, detail=detail) 
        return self
    def patient_id_is(self, id):
        # Verifica se as informações do paciente foram carregadas, caso contrário, tenta carregá-las.
        if self.patient_info == None:
            self.load_patient()
        # Compara o ID fornecido com o ID do paciente. Se forem diferentes, levanta uma ForbiddenException.
        if int(id) != self.patient_info.person_id:
            raise  ForbiddenException(detail="O paciente nao tem permissao de acessar este recurso.") 
    def if_patient_id_is(self, id):
        # Tenta carregar o paciente, mas não levanta exceção se não encontrar.
        if self.patient_info == None:
            self.load_patient(raise_exception=False)
        print(self.patient_info)
        # Se o paciente for encontrado, chama patient_id_is para verificar a permissão.
        if self.patient_info != None:
            self.patient_id_is(id)
        return self
    def if_specialist_has_patient(self, patient_id):
        # Tenta verificar se o especialista logado tem acesso ao paciente especificado.
        try: 
            if self.provider == None:
                self.load_specialist(raise_exception=True)
            try:
                # Busca o specialist_id associado ao patient_id.
                patient_specialist = VirtualPatient.objects().filter(patient_id=patient_id)[0]["specialist_id"]        
            except:
                # Se o paciente não existe, levanta uma ConflictException.
                raise ConflictException(detail="Paciente indicado nao existe")
            # Verifica se o ID do especialista logado corresponde ao specialist_id do paciente.
            self.specialist_id_is(patient_specialist)
        except:
            pass
@extend_schema(tags=["patients"])
class VirtualPatientViewSet(viewsets.ViewSet):
    # Define o queryset base para pacientes virtuais.
    queryset  = VirtualPatient.objects().all()
    # Define o serializer para pacientes virtuais.
    serializer_class = VirtualPatientSerializer
    def create(self, request, *args, **kwargs):
        # Inicializa o serializer com os dados da requisição.
        serializer = VirtualPatientSerializer(data=request.data)
        # Valida os dados do serializer, levantando exceção se houver erros.
        serializer.is_valid(raise_exception=True)
        # Instancia a classe UserAuth para gerenciar as permissões do usuário.
        auth = UserAuth(request.user)
        # Verifica se o usuário é um especialista e se tem permissão para criar um paciente com o specialist_id fornecido.
        auth.specialist_id_is(serializer.validated_data["specialist_id"])
        # Cria o paciente virtual no banco de dados.
        data = serializer.create(serializer.validated_data)         
        # Retorna a resposta com os dados do paciente criado e status 201 Created.
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        # Salva o objeto serializado. (Este método é usado por mixins, mas aqui a criação é personalizada no `create`).
        serializer.save()
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        # Obtém a instância do paciente virtual pelo ID (pk).
        instance = VirtualPatient.get(patient_id=pk)

        # Realiza verificações de permissão: se o usuário é o paciente ou o especialista associado.
        UserAuth(request.user) \
            .if_patient_id_is(int(pk)) \
            .if_specialist_id_is(instance["specialist_id"])
        # Obtém as comorbidades associadas ao paciente.
        comorbidities = VirtualPatient.get_comorbidities(patient_id=pk)
        # Adiciona as comorbidades à instância do paciente.
        instance["comorbidities"] = comorbidities
        # Retorna a instância do paciente com suas comorbidades.
        return Response(instance)


    def list(self, request, *args, **kwargs):
        # Obtém o parâmetro 'specialist_id' da query string.
        specialist_id = self.request.query_params.get('specialist_id')
        # Obtém todas as instâncias de pacientes virtuais.
        instances = VirtualPatient.objects().all()
        # Instancia a classe UserAuth para gerenciar as permissões do usuário.
        auth = UserAuth(request.user)
        # Carrega as informações do especialista logado.
        auth.load_specialist()
        # Se um specialist_id for fornecido, filtra as instâncias e verifica a permissão.
        if specialist_id != None and specialist_id != "":
            auth.specialist_id_is(specialist_id)
            instances = instances.filter(specialist_id=int(specialist_id))
        else:
            # Se nenhum specialist_id for fornecido, retorna um erro.
            raise ForbiddenException(detail="Se deve usar o query param filtrando pelo especialista, /patients?specialist_id={specialist_id}")
        # Para cada paciente, busca e adiciona suas comorbidades.
        for instance in instances:
            comorbidities = VirtualPatient.get_comorbidities(patient_id=instance["patient_id"])
            instance["comorbidities"] = comorbidities
        # Retorna a lista de pacientes.
        return Response(instances)
    

@extend_schema(tags=["wounds"])
class VirtualWoundViewSet(viewsets.ModelViewSet):
    # Define o queryset para feridas virtuais, anotando com a URL da imagem associada.
    queryset = VirtualWound.objects().annotate(
        image_url=Subquery(
            WoundImage.objects.filter(wound_id=OuterRef('wound_id')).values('image__image')
        )
    ).all()
    # Define o serializer para feridas virtuais.
    serializer_class = VirtualWoundSerializer
    
    def create(self, request, *args, **kwargs):
        # Inicializa o serializer com os dados da requisição.
        serializer = VirtualWoundSerializer(data=request.data)
        # Valida os dados do serializer, levantando exceção se houver erros.
        serializer.is_valid(raise_exception=True)
        # Obtém os dados validados.
        data = serializer.validated_data;
        # Define a data de atualização como a data e hora atuais.
        data["updated_at"] = datetime.datetime.now()
        # Instancia a classe UserAuth para gerenciar as permissões do usuário.
        auth = UserAuth(request.user)
        # Carrega as informações do especialista logado.
        auth.load_specialist()
        try:
            # Tenta obter o ID do especialista associado ao paciente fornecido.
            patient_specialist = VirtualPatient.objects().filter(patient_id=data["patient_id"])[0]["specialist_id"]        
        except:
            # Se o paciente não existe, retorna um erro de conflito.
            return Response({"detail": "Paciente indicado nao existe"}, status.HTTP_409_CONFLICT)
        # Verifica se o especialista logado tem permissão para criar uma ferida para o paciente especificado.
        auth.specialist_id_is(patient_specialist, "Especialista nao tem permissao de criar uma ferida para o paciente indicado")
        # Verifica se o especialista fornecido nos dados da ferida corresponde ao especialista do paciente.
        if(data["specialist_id"] != patient_specialist):
            return Response({"detail": "O especialista deve ser o mesmo do paciente"}, status=status.HTTP_409_CONFLICT)
    
        # Criar a ferida no banco usando o modelo virtual.
        instance = VirtualWound.create(data)
        
        # Se uma imagem foi enviada, criar o registro de imagem.
        if 'image' in request.FILES:
            image_serializer = ImageSerializer(data={'image': request.FILES['image']})
            if image_serializer.is_valid():
                image = image_serializer.save()
                WoundImage.objects.create(
                    wound_id=instance['wound_id'],
                    image=image
                )
        
        return Response(instance, status=status.HTTP_201_CREATED)
    def has_permission(self, request, instance):
        # Verifica as permissões para a instância da ferida: paciente e especialista.
        UserAuth(request.user) \
            .if_patient_id_is(instance["patient_id"]) \
            .if_specialist_id_is(instance["specialist_id"], detail="Especialista nao tem acesso a ferida solicitada")

    def retrieve(self, request, pk=None, *args, **kwargs):
        # Obtém a instância da ferida pelo ID (pk).
        instance = self.queryset.get(wound_id=pk)
        # Chama o método de verificação de permissão.
        self.has_permission(request, instance)
        # Se houver uma URL de imagem, constrói a URL absoluta.
        if instance.get("image_url"):
            instance["image_url"] = request.build_absolute_uri("../" + "media/" + instance.get("image_url"))

        # Serializa a instância.
        serializer = VirtualWoundSerializer(data=instance)
        serializer.is_valid(raise_exception=True)
        return Response(instance)

    def list(self, request: Request, *args, **kwargs):
        # Obtém todas as instâncias de feridas.
        instances = self.queryset.all()
        # Instancia a classe UserAuth para gerenciar as permissões do usuário.
        auth = UserAuth(request.user)
        # Obtém os parâmetros 'specialist_id' e 'patient_id' da query string.
        specialist_id = self.request.query_params.get('specialist_id')
        patient_id = self.request.query_params.get('patient_id')
        # Verifica se pelo menos um dos parâmetros é fornecido.
        if specialist_id in [None, ""] and patient_id in [None, ""]:
            return Response({"detail": "Eh nescessario o query param specialist_id ou patient_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Se 'specialist_id' for fornecido, filtra e verifica permissão.
        if specialist_id not in [None, ""]:
            auth.if_specialist_id_is(specialist_id)
            instances = instances.filter(specialist_id=int(specialist_id))
        # Se 'patient_id' for fornecido, filtra e verifica permissão.
        if patient_id not in [None, ""]:
            auth.if_patient_id_is(patient_id)
            auth.if_specialist_has_patient(patient_id)
            instances = instances.filter(patient_id=int(patient_id))

        # Para cada instância, se houver URL de imagem, constrói a URL absoluta.
        for instance in instances:            
            if instance.get("image_url"):
                instance["image_url"] = request.build_absolute_uri("../" + "media/" + instance.get("image_url"))
        # Serializa a lista de instâncias.
        serializer = VirtualWoundSerializer(many=True, data=list(instances))
        serializer.is_valid(raise_exception=True)
        return Response(instances)
      
      # Método `update` implementado na View

    def update(self, request, pk=None, *args, **kwargs):
        # 1. Obtém a instância existente da ferida.
        instance = VirtualWound.get(wound_id=pk)
        # Verifica as permissões do usuário para a instância.
        self.has_permission(request, instance)
        if not instance:
            return Response({'error': 'Wound not found'}, status=status.HTTP_404_NOT_FOUND)

        # 2. Instancia o serializer com os dados existentes e os dados da requisição.
        #    `partial=kwargs.get('partial', False)` permite que o mesmo método `update`
        #    lida com PUT (false) e PATCH (true) automaticamente.
        serializer = self.get_serializer(instance=instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # 3. Prepara os dados para atualização no modelo VirtualWound.
            update_data = {
                "wound_id": instance["wound_id"], 
                "updated_at": datetime.datetime.now() 
            }

            # Copia apenas os campos válidos e atualizáveis do serializer para update_data.
            for field_name in [
                "patient_id", "specialist_id", "region", "wound_type",
                "start_date", "end_date", "is_active", "image_id"
            ]:
                if field_name in serializer.validated_data:
                    update_data[field_name] = serializer.validated_data[field_name]
                # Se for PATCH e o campo não estiver em validated_data, seu valor será mantido.

            # 4. Chama o método .update() do seu VirtualWound para persistir as mudanças no OMOP.
            updated_instance_data = VirtualWound.update(update_data)

            # 5. Lida com a atualização da imagem, se um novo arquivo for enviado.
            if 'image' in request.FILES:
                image_serializer = ImageSerializer(data={'image': request.FILES['image']})
                if image_serializer.is_valid(raise_exception=True):
                    new_image = image_serializer.save() # Salva a nova imagem no sistema de arquivos/DB

                    # Tenta encontrar e atualizar o registro WoundImage existente.
                    try:
                        wound_image_record = WoundImage.objects.get(wound_id=updated_instance_data['wound_id'])
                        wound_image_record.image = new_image
                        wound_image_record.save()
                    except WoundImage.DoesNotExist:
                        # Se não havia um registro de imagem associado, cria um novo.
                        WoundImage.objects.create(
                            wound_id=updated_instance_data['wound_id'],
                            image=new_image
                        )

        return Response(updated_instance_data)
    @transaction.atomic()
    def partial_update(self, request, pk=None, *args, **kwargs):
        # Obtém a instância da ferida pelo ID (pk).
        instance = VirtualWound.get(wound_id=pk)
        # Verifica as permissões do usuário para a instância.
        self.has_permission(request, instance)
        if not instance:
            return Response({'error': 'Wound not found'}, status=status.HTTP_404_NOT_FOUND)

        # Inicializa o serializer com os dados da requisição, permitindo atualização parcial.
        serializer = VirtualWoundSerializer(data=request.data , partial=True)
        serializer.is_valid(raise_exception=True)

        # Prepara os dados para atualização, mantendo os dados existentes e atualizando a data de modificação.
        update_data = {
            **instance, 
            "updated_at": datetime.datetime.now() 
        }

        # Copia apenas os campos validados do serializer para os dados de atualização.
        for field_name in [
            "patient_id", "specialist_id", "region", "wound_type",
            "start_date", "end_date", "is_active", "image_id"
        ]:
            if field_name in serializer.validated_data:
                update_data[field_name] = serializer.validated_data[field_name]
            # Se for PATCH e o campo não estiver em validated_data, seu valor será mantido.

        # 4. Chama o método .update() do seu VirtualWound para persistir as mudanças no OMOP.
        updated_instance_data = VirtualWound.update(update_data)

        # 5. Lida com a atualização da imagem, se um novo arquivo for enviado.
        if 'image' in request.FILES:
            image_serializer = ImageSerializer(data={'image': request.FILES['image']})
            if image_serializer.is_valid(raise_exception=True):
                new_image = image_serializer.save() # Salva a nova imagem no sistema de arquivos/DB

                # Tenta encontrar e atualizar o registro WoundImage existente.
                try:
                    wound_image_record = WoundImage.objects.get(wound_id=updated_instance_data['wound_id'])
                    wound_image_record.image = new_image
                    wound_image_record.save()
                except WoundImage.DoesNotExist:
                    # Se não havia um registro de imagem associado, cria um novo.
                    WoundImage.objects.create(
                        wound_id=updated_instance_data['wound_id'],
                        image=new_image
                    )

        return Response(updated_instance_data)
    @action(detail=True, methods=['put'], url_path='archive', serializer_class=None)
    def archive(self, request, pk=None):
        # Obtém a instância da ferida pelo ID (pk).
        instance = VirtualWound.get(wound_id=pk)
        # Verifica as permissões do usuário para a instância.
        self.has_permission(request, instance)
        if not instance:
            return Response({'error': 'Wound not found'}, status=status.HTTP_404_NOT_FOUND)
        # Marcar a ferida como inativa usando o Concept ID apropriado.
        instance["is_active"] = False
        # Atualiza a ferida no banco de dados.
        updated_instance = VirtualWound.update(data=instance)
        
        return Response(updated_instance)
    
@extend_schema(tags=["tracking-records"])
class VirtualTrackingRecordsViewSet(viewsets.ModelViewSet):
    # Define o queryset para registros de acompanhamento, anotando com a URL da imagem.
    queryset = VirtualTrackingRecords.objects().all().annotate(
        image_url=Subquery(
            TrackingRecordImage.objects.filter(tracking_record_id=OuterRef('tracking_id')).values('image__image')
        )
    )
    # Define o serializer para registros de acompanhamento.
    serializer_class = VirtualTrackingRecordsSerializer

    def has_permission(self, request, data):
        # Verifica as permissões do usuário para os dados fornecidos (paciente e especialista).
        UserAuth(request.user) \
            .if_patient_id_is(data["patient_id"]) \
            .if_specialist_id_is(data["specialist_id"]) 
    def create(self, request, *args, **kwargs):
        # Inicializa o serializer com os dados da requisição.
        serializer = VirtualTrackingRecordsSerializer(data=request.data)
        # Valida os dados do serializer, levantando exceção se houver erros.
        serializer.is_valid(raise_exception=True)
        # Obtém os dados validados.
        data_to_create = serializer.validated_data
        # Obtém a ferida associada ao registro de acompanhamento.
        wound = VirtualWound.get(wound_id=int(data_to_create["wound_id"]))
        # Atribui o especialista e paciente da ferida ao registro de acompanhamento.
        data_to_create["specialist_id"] = wound["specialist_id"]
        data_to_create["patient_id"] = wound["patient_id"]
        # Verifica as permissões do usuário.
        self.has_permission(request, data_to_create)

        # Define a data do registro como a data atual.
        data_to_create["track_date"] = datetime.date.today()
        # Define campos vazios se não forem fornecidos.
        if(data_to_create.get("extra_notes", None) == None):
            data_to_create["extra_notes"] = ""
        if(data_to_create.get("guidelines_to_patient", None) == None):
            data_to_create["guidelines_to_patient"] = ""
        # Cria o registro de acompanhamento.
        data = VirtualTrackingRecords.create(data_to_create)
        return Response(data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        # Obtém a instância do registro de acompanhamento pelo ID (pk).
        instance = self.queryset.get(tracking_id=pk)
        # Verifica as permissões do usuário.
        self.has_permission(request, instance)
        # Constrói a URL absoluta da imagem.
        instance["image_url"] = request.build_absolute_uri("../" +"media/"+ instance.get("image_url"))
        return Response(instance)


    def list(self, request: Request, *args, **kwargs):
        # Obtém todas as instâncias de registros de acompanhamento.
        instances = self.queryset.all()
        # Instancia a classe UserAuth para gerenciar as permissões do usuário.
        auth = UserAuth(request.user)
        # Obtém os parâmetros de filtro da query string.
        specialist_id = self.request.query_params.get('specialist_id')
        patient_id = self.request.query_params.get('patient_id')
        wound_id = self.request.query_params.get('wound_id')
        # Verifica se pelo menos um parâmetro de filtro é fornecido.
        if specialist_id in [None, ""] and patient_id in [None, ""] and wound_id in [None, ""]:
            return Response({"detail": "Eh nescessario o query param specialist_id, patient_id ou wound_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtra as instâncias com base no specialist_id, se fornecido.
        if specialist_id not in [None, ""]:
            auth.if_specialist_id_is(specialist_id)
            instances = instances.filter(specialist_id=int(specialist_id))
        # Filtra as instâncias com base no patient_id, se fornecido.
        if patient_id not in [None, ""]:
            auth.if_patient_id_is(patient_id)
            instances = instances.filter(patient_id=int(patient_id))
        # Filtra as instâncias com base no wound_id, se fornecido.
        if wound_id not in [None, ""]:
            instances = instances.filter(wound_id=int(wound_id))
        instances = list(instances)
        # Para cada instância, se houver URL de imagem, constrói a URL absoluta.
        for instance in instances:
            if instance.get("image_url", None) != None:
                instance["image_url"] = request.build_absolute_uri("../" +"media/"+ instance.get("image_url"))
        return Response(instances)
    
@extend_schema(tags=["tracking-records"])
class TrackingRecordsImageViewSet(viewsets.ViewSet):
    # Define o serializer para imagens.
    serializer_class = ImageSerializer
    # Define os parsers de requisição, permitindo o upload de arquivos.
    parser_classes = [MultiPartParser]
    def update(self, request,pk, *args, **kwargs):
        # Inicializa o serializer com os dados da requisição.
        serializer = ImageSerializer(data=request.data)
        # Valida os dados do serializer, levantando exceção se houver erros.
        serializer.is_valid(raise_exception=True)
        try: 
            # Obtém a instância da imagem do registro de acompanhamento.
            tracking_image_instance = TrackingRecordImage.objects.get(tracking_record_id=pk)
            # Obtém a instância do registro de acompanhamento virtual.
            tracking_record_instance = VirtualTrackingRecords.get(tracking_id=pk)
            # Verifica as permissões do usuário para o registro de acompanhamento.
            UserAuth(request.user) \
                .if_patient_id_is(tracking_record_instance["patient_id"]) \
                .if_specialist_id_is(tracking_record_instance["specialist_id"]) 
            # Salva a nova imagem.
            image_instance = serializer.save()
            # Associa a nova imagem ao registro de acompanhamento.
            tracking_image_instance.image = image_instance
            tracking_image_instance.save()

            uploaded_image = request.FILES.get("image")
            if uploaded_image is None:
                return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Abre a imagem usando PIL e a converte para RGB.
            pil_image = PILImage.open(uploaded_image).convert("RGB")

            # Realiza predições na imagem.
            tissue_prediction = predict_image_class(pil_image)
            multihead_predictions = predict_multi_label(pil_image)
            #wound_pixels = count_pixels_simple(model_path="wound_segmentation_model2.hdf5",image_path=pil_image,threshold=0.5)
            #reference_pixels = get_reference_area(pil_image)
            #reference_diameter = 7
            #reference_size = 3,14*(reference_diameter/2)^2
            #wound_size = wound_pixels*reference_size/reference_pixels

        except TrackingRecordImage.DoesNotExist:
            return Response({"error": "Tracking record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
                "message": "Image updated successfully",
                "predictions": {
                    "tissue_type": tissue_prediction,
                    "W_I_Fi": multihead_predictions,
                    #"Wound Size(cm^2)": wound_size
                }
            }, status=status.HTTP_200_OK)

@extend_schema(tags=["wounds"])
class WoundImageViewSet(viewsets.ViewSet):
    # Define o serializer para imagens.
    serializer_class = ImageSerializer
    # Define os parsers de requisição, permitindo o upload de arquivos.
    parser_classes = [MultiPartParser]

    def update(self, request,pk, *args, **kwargs):
        # Inicializa o serializer com os dados da requisição.
        serializer = ImageSerializer(data=request.data)
        # Valida os dados do serializer, levantando exceção se houver erros.
        serializer.is_valid(raise_exception=True)

        try: 
            # Obtém a instância da imagem da ferida.
            wound_image_instance = WoundImage.objects.get(wound_id=pk)
            # Obtém a instância da ferida virtual.
            wound_instance = VirtualWound.get(wound_id=pk)
            # Verifica as permissões do usuário para a ferida.
            UserAuth(request.user) \
                .if_patient_id_is(wound_instance["patient_id"]) \
                .if_specialist_id_is(wound_instance["specialist_id"])
            # Salva a nova imagem.
            image_instance = serializer.save()
            # Associa a nova imagem à ferida.
            wound_image_instance.image = image_instance
            wound_image_instance.save()

            uploaded_image = request.FILES.get('image')
            if uploaded_image is None:
                return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Abre a imagem usando PIL e a converte para RGB.
            pil_image = PILImage.open(uploaded_image).convert("RGB")

            # Realiza predições na imagem.
            tissue_prediction = predict_image_class(pil_image)
            multihead_predictions = predict_multi_label(pil_image)
            #wound_pixels = count_pixels_simple(model_path="wound_segmentation_model2.hdf5",image_path=pil_image,threshold=0.5)
            #reference_pixels = get_reference_area(pil_image)
            #reference_diameter = 7
            #reference_size = 3,14*(reference_diameter/2)^2
            #wound_size = wound_pixels*reference_size/reference_pixels

        except WoundImage.DoesNotExist:
            return Response({"error": "Tracking record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
                "message": "Image updated successfully",
                "predictions": {
                    "tissue_type": tissue_prediction,
                    "W_I_Fi": multihead_predictions,
                    #"Wound Size(cm^2)": wound_size
                }
            }, status=status.HTTP_200_OK)

@extend_schema(tags=["comorbidities"])
class VirtualComorbidityViewSet(viewsets.ModelViewSet):
    # Define o queryset para comorbidades virtuais.
    queryset = VirtualComorbidity.objects().all()
    # Define o serializer para comorbidades virtuais.
    serializer_class = VirtualComorbiditySerializer
    
    def get_queryset(self):
        # Obtém todas as comorbidades.
        queryset = VirtualComorbidity.objects().all()
        # Obtém o parâmetro 'patient_id' da query string.
        patient_id = self.request.query_params.get('patient_id', None)
        # Se 'patient_id' for fornecido, filtra o queryset.
        if patient_id is not None:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset
        
    def create(self, request, *args, **kwargs):
        """
        Método personalizado para criar comorbidades garantindo que o conceito exista
        """
        # Inicializa o serializer com os dados da requisição.
        serializer = self.get_serializer(data=request.data)
        # Valida os dados do serializer, levantando exceção se houver erros.
        serializer.is_valid(raise_exception=True)
        
        # Já validamos o comorbidity_type no serializer.
        self.perform_create(serializer)
        # Obtém os cabeçalhos de sucesso para a resposta.
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)