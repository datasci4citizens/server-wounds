from rest_framework import serializers, viewsets, routers, parsers
from django.urls import path, include
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from app_cicatrizando.google import google_get_user_data
from .omop_models import Provider


# --- VIEWSETS ---


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
        user, created = User.objects.get_or_create(
            email=user_data.get("email"),
            defaults={
                "username": user_data.get("email"),
                "first_name": user_data.get("given_name"),
                "last_name": user_data.get("family_name", ""),
            }
        )

        # Check for existing provider record (OMOP model) only
        provider_id = None
        provider_data = None
        try:
            provider = Provider.objects.get(email=user.email)
            provider_id = provider.provider_id
            provider_data = {
                'provider_id': provider.provider_id,
                'provider_name': provider.provider_name,
                'specialty': provider.specialty_concept_id
            }
        except Provider.DoesNotExist:
            pass
        
        # Determine role and profile completion status
        is_provider = provider_id is not None
        role = "specialist" if is_provider else "user"
        profile_completion_required = created or not is_provider

        # Generate JWT token
        token = RefreshToken.for_user(user)
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
