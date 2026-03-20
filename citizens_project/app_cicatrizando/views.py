from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from datetime import date
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .google import google_get_user_data
from .models import WoundsUser, Provider
from .serializers import AuthSerializer, AuthTokenResponseSerializer
import logging

logger = logging.getLogger("app_cicatrizando")
DEFAULT_BIRTH_DATE = date(1900, 1, 1)

User = get_user_model()


class MeView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        if user.is_anonymous:
            return Response({"message": "Não autenticado", "authenticated": False})

        wounds_user_name = None
        if hasattr(user, "wounds_user"):
            wounds_user_name = user.wounds_user.name

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": wounds_user_name,
            "authenticated": True
        })


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

        user_data = google_get_user_data(validated_data)
        logger.debug(f"User data from Google: {user_data}")

        user_email = user_data.get("email")
        full_name = user_data.get("name") or f"{user_data.get('given_name', '')} {user_data.get('family_name', '')}".strip() or user_email
        birth_date = validated_data.get("birth_date")
        if birth_date is None:
            birth_date = DEFAULT_BIRTH_DATE

        user, created = User.objects.get_or_create(username=user_email, email=user_email)
        user_update_fields = []
        if user.email != user_email:
            user.email = user_email
            user_update_fields.append("email")
        if user_update_fields:
            user.save(update_fields=user_update_fields)

        selected_role = validated_data.get("role", WoundsUser.Patient)

        wounds_user, wounds_user_created = WoundsUser.objects.get_or_create(
            user=user,
            defaults={
                "name": full_name,
                "email": user_email,
                "birth_date": birth_date,
                "role": selected_role,
            },
        )


        # user exists
        if not wounds_user_created:
            update_fields = []
            if selected_role and (wounds_user.role != selected_role):
                wounds_user.role = selected_role
                update_fields.append("role")

            if full_name and (wounds_user.name != full_name):
                wounds_user.name = full_name
                update_fields.append("name")
            if wounds_user.email != user_email:
                wounds_user.email = user_email
                update_fields.append("email")
            if wounds_user.birth_date != birth_date:
                wounds_user.birth_date = birth_date
                update_fields.append("birth_date")
                
            if update_fields:
                wounds_user.save(update_fields=update_fields)

        patient_data = None
        provider_data = None

        if wounds_user.role == WoundsUser.Provider:
            provider, _ = Provider.objects.get_or_create(wounds_user=wounds_user)
            provider_data = {
                "provider_id": provider.pk,
                "provider_name": wounds_user.name,
            }
        else:
            patient_data = {
                "patient_id": wounds_user.pk,
                "patient_name": wounds_user.name,
            }

        token = RefreshToken.for_user(user)

        is_provider = provider_data is not None
        is_patient = patient_data is not None
        role = "provider" if is_provider else ("patient" if is_patient else "user")
        profile_completion_required = created or wounds_user_created

        response = {
            "access": str(token.access_token),
            "refresh": str(token),
            "role": role,
            "is_new_user": created or wounds_user_created,
            "patient_data": patient_data,
            "provider_data": provider_data,
            "profile_completion_required": profile_completion_required
        }

        return Response(response, status=200)
