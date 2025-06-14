from rest_framework import serializers, viewsets, routers, parsers
from django.urls import path, include
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from app_cicatrizando.google import google_get_user_data
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


User = get_user_model()

# Just a test endpoint to check if the user is logged in and return user info
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


class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    
class AuthTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    role = serializers.CharField()
    is_new_user = serializers.BooleanField()
    specialist_id = serializers.IntegerField(allow_null=True)
    provider_id = serializers.IntegerField(allow_null=True)
    profile_completion_required = serializers.BooleanField()

class BindCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_null=False, allow_blank=False)
class BindSerializer(serializers.Serializer):
    code = serializers.IntegerField(allow_null=False)
    email = serializers.EmailField()

base_string = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def to_base(number, base):
    result = ""
    while number:
        result += base_string[number % base]
        number //= base
    return result[::-1] or "0"

class UserPatientBindView(viewsets.ViewSet):
    serializer_class = BindCodeSerializer
    @transaction.atomic
    @extend_schema(request=BindSerializer, responses={200: AuthTokenResponseSerializer})
    def create(self, request, *args, **kwargs):
        serializer = BindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            email = data["email"]
            patient = PatientNonClinicalInfos.objects.filter(bind_code=data["code"]).get()
            patient.user = User.objects.get(email=email)
            patient.bind_code = None
            patient.user.save()
            patient.save()
        except PatientNonClinicalInfos.DoesNotExist:
            return Response("Codigo invalido", status=status.HTTP_404_NOT_FOUND)
        
        return Response(patient.person_id,status=status.HTTP_200_OK)
    
    @action(detail=True, url_path="new", methods=['post'])
    def new_patient_bind(self, request, pk : int, *args, **kwargs):
        try:
            patient = PatientNonClinicalInfos.objects.filter(person_id=pk).get()
            patient.bind_code = random.randrange(0, 1048576)
            patient.save()
        except PatientNonClinicalInfos.DoesNotExist:
            return Response("Paciente não existe",status=status.HTTP_404_NOT_FOUND)
        return Response(patient.bind_code)
class GoogleLoginView(viewsets.ViewSet):
    serializer_class = AuthSerializer
    permission_classes = [AllowAny]        

    @extend_schema(request=AuthSerializer, responses={200: AuthTokenResponseSerializer})
    def create(self, request, *args, **kwargs):
        auth_serializer = self.serializer_class(data=request.data)
        auth_serializer.is_valid(raise_exception=True)
        validated_data = auth_serializer.validated_data
        user_data = google_get_user_data(validated_data)

        # Creates user in DB if first time login
        user_email  = user_data.get("email")
        # Check for existing provider record (OMOP model) only
        provider_id = None
        provider_data = None
        user, created = User.objects.get_or_create(username=user_email,email=user_email)
        try:
            provider = VirtualSpecialist.objects().filter(user_id=user.id).get()
            print(provider)
            provider_id = provider["specialist_id"]
            provider_data = {
                'provider_id': provider["specialist_id"],
                'provider_name': provider["specialist_name"],
                'specialty': provider["speciality"]
            }
        except Provider.DoesNotExist:
            pass
        token = RefreshToken.for_user(user)
        
        # Determine role and profile completion status
        is_provider = provider_id is not None
        role = "specialist" if is_provider else "user"
        profile_completion_required = created or not is_provider

        # Generate JWT token
        response = {
            "access": str(token.access_token),
            "refresh": str(token),
            "role": role,
            "is_new_user": created,
            "specialist_id": None,  # Always None since we no longer check this model
            "provider_id": provider_id,
            "provider_data": provider_data,
            "profile_completion_required": profile_completion_required
        }

        return Response(response, status=200)
