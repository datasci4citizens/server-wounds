from rest_framework import serializers, viewsets
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .google import google_get_user_data
from .models import PatientNonClinicalInfos
import logging

logger = logging.getLogger("app_saude")

User = get_user_model()


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
    patient_data = serializers.DictField(allow_null=True)
    profile_completion_required = serializers.BooleanField()


# ViewSet para verificar o status de autenticação do usuário.
class MeView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        if user.is_anonymous:
            return Response({"message": "Não autenticado", "authenticated": False})
        
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "authenticated": True
        })


# ViewSet para lidar com o login via Google.
class GoogleLoginView(viewsets.ViewSet):
    serializer_class = AuthSerializer
    permission_classes = [AllowAny]

    @extend_schema(request=AuthSerializer, responses={200: AuthTokenResponseSerializer})
    def create(self, request, *args, **kwargs):
        logger.debug("Google login request")
        auth_serializer = self.serializer_class(data=request.data)
        auth_serializer.is_valid(raise_exception=True)
        validated_data = auth_serializer.validated_data
        logger.debug(f"Validated data: {validated_data}")
        
        # Obtém os dados do usuário do Google
        user_data = google_get_user_data(validated_data)
        logger.debug(f"User data from Google: {user_data}")

        # Cria ou obtém o usuário no banco de dados local
        user_email = user_data.get("email")
        user, created = User.objects.get_or_create(username=user_email, email=user_email)
        
        patient_data = None
        try:
            logger.debug(f"Fetching patient non-clinical info for user {user.id}")
            patient_info = PatientNonClinicalInfos.objects.filter(user=user).get()
            logger.debug(f"Patient info found: {patient_info}")
            patient_data = {
                'patient_id': patient_info.person_id,
                'patient_name': patient_info.name
            }
        except PatientNonClinicalInfos.DoesNotExist:
            pass

        # Gera um token JWT para o usuário
        token = RefreshToken.for_user(user)
        
        # Determina o papel do usuário
        is_patient = patient_data is not None
        role = "patient" if is_patient else "user"
        profile_completion_required = created or not is_patient

        # Constrói a resposta com os tokens JWT e informações do usuário
        response = {
            "access": str(token.access_token),
            "refresh": str(token),
            "role": role,
            "is_new_user": created,
            "patient_data": patient_data,
            "profile_completion_required": profile_completion_required
        }

        return Response(response, status=200)
