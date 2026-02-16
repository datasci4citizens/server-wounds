from rest_framework import serializers, viewsets, routers, parsers
from django.urls import path, include
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from app_cicatrizando.google import google_get_user_data
from .virtual_views import UserAuth
from .models import PatientNonClinicalInfos
from .virtual_models import VirtualSpecialist
from .omop.omop_models import Provider
from rest_framework.decorators import action
import hashlib
import base64
import random
from django.db import transaction
# --- VIEWSETS ---
from django.contrib.auth.models import AnonymousUser
import logging
logger = logging.getLogger("app_saude")


# Obtém o modelo de usuário ativo do Django.
User = get_user_model()


# ViewSet para verificar o status de autenticação do usuário.
class MeView(viewsets.ViewSet):
    # Requer que o usuário esteja autenticado para acessar esta view.
    permission_classes = [IsAuthenticated]

    # Lista as informações do usuário logado.
    def list(self, request):
        user = request.user
        # Verifica se o usuário é anônimo (não autenticado).
        if user.is_anonymous:
            return Response({"message": "Não autenticado", "authenticated": False})
        
        # Retorna informações básicas do usuário se autenticado.
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "authenticated": True
        })


# Serializador para dados de autenticação (código ou token).
class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_null=False, allow_blank=False)
    token = serializers.CharField(required=False, allow_null=False, allow_blank=False)

# Serializador para a resposta de token de autenticação.
class AuthTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    role = serializers.CharField()
    is_new_user = serializers.BooleanField()
    specialist_id = serializers.IntegerField(allow_null=True)
    provider_id = serializers.IntegerField(allow_null=True)
    profile_completion_required = serializers.BooleanField()

# Serializador para o código de vínculo.
class BindCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_null=False, allow_blank=False)

# Serializador para vincular um código a um email.
class BindSerializer(serializers.Serializer):
    code = serializers.IntegerField(allow_null=False)
    email = serializers.EmailField()

# String base para conversão de número para base alfanumérica.
base_string = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# Função para converter um número para uma string em uma base específica.
def to_base(number, base):
    result = ""
    while number:
        result += base_string[number % base]
        number //= base
    return result[::-1] or "0"

# ViewSet para gerenciar o vínculo entre usuários e pacientes.
class UserPatientBindView(viewsets.ViewSet):
    serializer_class = BindCodeSerializer # Serializador padrão para esta view.

    # Endpoint para vincular um paciente a um usuário existente através de um código.
    @transaction.atomic # Garante que a operação seja atômica no banco de dados.
    @extend_schema(request=BindSerializer, responses={200: AuthTokenResponseSerializer})
    def create(self, request, *args, **kwargs):
        serializer = BindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Valida os dados da requisição.
        data = serializer.validated_data
        try:
            email = data["email"]
            # Verifica se o email fornecido corresponde ao email do usuário autenticado.
            if email != request.user.email:
                return Response({"detail": "O email deve ser o mesmo do usuario atual"}, status=status.HTTP_403_FORBIDDEN)
            # Busca o paciente pelo código de vínculo.
            patient = PatientNonClinicalInfos.objects.filter(bind_code=data["code"]).get()
            # Associa o paciente ao usuário atual e remove o código de vínculo.
            patient.user = User.objects.get(email=email)
            patient.bind_code = None
            patient.user.save()
            patient.save()
        except PatientNonClinicalInfos.DoesNotExist:
            return Response("Codigo invalido", status=status.HTTP_404_NOT_FOUND) # Retorna erro se o código for inválido.
        
        return Response(patient.person_id,status=status.HTTP_200_OK) # Retorna o ID da pessoa se o vínculo for bem-sucedido.
    
    # Action para gerar um novo código de vínculo para um paciente existente.
    @action(detail=True, url_path="new", methods=['post'])
    def new_patient_bind(self, request, pk : int, *args, **kwargs):
        auth = UserAuth(request.user) # Inicializa a classe de autenticação do usuário.
        auth.load_specialist() # Carrega informações do especialista associado.
        try:
            # Busca o paciente pelo ID.
            patient = PatientNonClinicalInfos.objects.filter(person_id=pk).get()
            # Verifica se o especialista tem permissão para acessar este paciente.
            auth.if_specialist_has_patient(patient.person_id)
            # Gera um novo código de vínculo aleatório e salva.
            patient.bind_code = random.randrange(0, 1048576)
            patient.save()
        except PatientNonClinicalInfos.DoesNotExist:
            return Response("Paciente não existe",status=status.HTTP_404_NOT_FOUND) # Retorna erro se o paciente não for encontrado.
        return Response(patient.bind_code) # Retorna o novo código de vínculo.

# ViewSet para lidar com o login via Google.
class GoogleLoginView(viewsets.ViewSet):
    serializer_class = AuthSerializer # Serializador para os dados de autenticação do Google.
    permission_classes = [AllowAny] # Permite acesso sem autenticação.       

    # Endpoint para autenticar usuários via Google.
    @extend_schema(request=AuthSerializer, responses={200: AuthTokenResponseSerializer})
    def create(self, request, *args, **kwargs):
        logger.debug("Google login request")
        auth_serializer = self.serializer_class(data=request.data)
        auth_serializer.is_valid(raise_exception=True) # Valida os dados da requisição.
        validated_data = auth_serializer.validated_data
        logger.debug(f"Validated data: {validated_data}")
        # Obtém os dados do usuário do Google.
        user_data = google_get_user_data(validated_data)
        logger.debug(f"User data from Google: {user_data}")

        # Cria ou obtém o usuário no banco de dados local.
        user_email  = user_data.get("email")
        provider_id = None
        provider_data = None
        user, created = User.objects.get_or_create(username=user_email,email=user_email)
        try:
            logger.debug(f"Fetching provider for user {user.id}")
            # Tenta encontrar um especialista virtual associado ao usuário.
            provider = VirtualSpecialist.objects().filter(user_id=user.id).get()
            print(provider)
            provider_id = provider["specialist_id"]
            logger.debug(f"Provider found: {provider}")
            provider_data = {
                'provider_id': provider["specialist_id"],
                'provider_name': provider["specialist_name"],
                'specialty': provider["speciality"]
            }
        except Provider.DoesNotExist:
            pass # Continua se nenhum provedor for encontrado.
        
        patient_data = None
        try :
            logger.debug(f"Fetching patient non-clinical info for user {user.id}")
            # Tenta encontrar informações não-clínicas do paciente associadas ao usuário.
            patient_info = PatientNonClinicalInfos.objects.filter(user=user).get()
            logger.debug(f"Patient info found: {patient_info}")
            patient_data = {
                'patient_id': patient_info.person_id,
                'patient_name': patient_info.name
            }
        except PatientNonClinicalInfos.DoesNotExist:
            pass # Continua se nenhuma informação de paciente for encontrada.

        # Gera um token JWT de atualização para o usuário.
        token = RefreshToken.for_user(user)
        
        # Determina o papel do usuário e se o preenchimento do perfil é necessário.
        is_provider = provider_id is not None
        is_patient = patient_data is not None
        
        if is_provider:
            role = "specialist"
        elif is_patient:
            role = "patient"
        else:
            role = "user" # Papel padrão se não for especialista nem paciente.
            
        profile_completion_required = created or (not is_provider and not is_patient) # Requer preenchimento se for novo usuário ou não tiver papel definido.

        # Constrói a resposta com os tokens JWT e informações do usuário.
        response = {
            "access": str(token.access_token),
            "refresh": str(token),
            "role": role,
            "is_new_user": created,
            "specialist_data": provider_data,
            "patient_data": patient_data,
            "profile_completion_required": profile_completion_required
        }

        return Response(response, status=200) # Retorna a resposta de autenticação.