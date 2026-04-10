from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .google import google_get_user_data
from .models import WoundsUser, Provider
from .serializers import (
    GoogleAuthSerializer,
    GoogleAuthResponseSerializer,
    SpecialistRegistrationSerializer,
    SpecialistRegistrationResponseSerializer,
    MeResponseSerializer,
)
import logging

logger = logging.getLogger("app_cicatrizando")

User = get_user_model()


def _is_registration_complete(user):
    """
    Check if user has completed registration.
    Registration is complete when:
    - WoundsUser exists with a role set
    - If role is Provider, Provider record exists
    - If role is Patient, Patient record exists
    """
    try:
        wounds_user = user.wounds_user
    except WoundsUser.DoesNotExist:
        return False
    
    if not wounds_user.role:
        return False
    
    if wounds_user.role == WoundsUser.Provider:
        return Provider.objects.filter(wounds_user=user).exists()
    elif wounds_user.role == WoundsUser.Patient:
        return Patient.objects.filter(wounds_user=user).exists()



def _get_user_role_display(wounds_user:  WoundsUser) -> str: 
    """Convert role code to display string."""
    if not wounds_user or not wounds_user.role:
        return None
    return "specialist" if wounds_user.role == WoundsUser.Provider else "patient"


class GoogleLoginView(viewsets.ViewSet):
    """
    Google OAuth authentication endpoint.
    
    Exchanges Google auth code for JWT tokens.
    Returns 201 for new users, 200 for existing users.
    """
    serializer_class = GoogleAuthSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        request=GoogleAuthSerializer,
        responses={
            200: GoogleAuthResponseSerializer,
            201: GoogleAuthResponseSerializer,
        }
    )

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user_data = google_get_user_data(validated_data["auth_code"])
        logger.debug(f"User data from Google: {user_data}")

        user_email = user_data.get("email")
        full_name = (
            user_data.get("name") or
            f"{user_data.get('given_name', '')} {user_data.get('family_name', '')}".strip() or
            user_email.split('@')[0]
        )

        user, user_created = User.objects.get_or_create(
            username=user_email,
            defaults={"email": user_email}
        )

        if user.email != user_email:
            user.email = user_email
            user.save(update_fields=["email"])

        wounds_user, wounds_user_created = WoundsUser.objects.get_or_create(
            user=user,
            defaults={}
        )

        is_new = user_created or wounds_user_created
        registration_complete = _is_registration_complete(user)

        token = RefreshToken.for_user(user)

        response_data = {
            "access": str(token.access_token),
            "refresh": str(token),
            "email": user.email,
            "full_name": full_name,
            "registration_complete": registration_complete,
            "role": _get_user_role_display(wounds_user),
        }

        status_code = status.HTTP_201_CREATED if is_new else status.HTTP_200_OK
        return Response(response_data, status=status_code)


class SpecialistRegistrationView(viewsets.ViewSet):
    """
    Complete specialist registration.
    
    Sets user role to Specialist and creates professional profile.
    Requires JWT authentication.
    """
    serializer_class = SpecialistRegistrationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SpecialistRegistrationSerializer,
        responses={
            200: SpecialistRegistrationResponseSerializer,
            201: SpecialistRegistrationResponseSerializer,
        }
        
    )
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user

        wounds_user, _ = WoundsUser.objects.get_or_create(user=user)
        
        wounds_user.name = data["name"]
        wounds_user.birth_date = data["birth_date"]
        wounds_user.state = data["state"]
        wounds_user.city = data["city"]
        wounds_user.role = WoundsUser.Provider
        wounds_user.save()

        provider, _ = Provider.objects.update_or_create(
            wounds_user=user,
            defaults={
                "professional_id": data["professional_id"],
                "contact_phone": data.get("contact_phone", ""),
                "contact_email": data.get("contact_email", ""),
            }
        )

        response_data = {
            "message": "Specialist registered successfully",
            "user": {
                "id": wounds_user.pk,
                "name": wounds_user.name,
                "birth_date": wounds_user.birth_date.isoformat(),
                "state": wounds_user.state,
                "city": wounds_user.city,
                "role": "specialist",
            },
            "specialist": {
                "id": provider.pk,
                "professional_id": provider.professional_id,
                "contact_phone": provider.contact_phone,
                "contact_email": provider.contact_email,
            },
        }

    
        return Response(response_data, status=status.HTTP_201_CREATED)

class MeView(viewsets.ViewSet):
    """
    Get current user's complete profile.
    
    Returns user data including role-specific information.
    Requires JWT authentication.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: MeResponseSerializer})
    def list(self, request):
        user = request.user
        
        wounds_user = user.wounds_user
        
        specialist_data = None
        patient_data = None
        if wounds_user.role == WoundsUser.Provider:
            try:
                provider = user.provider
                specialist_data = {
                    "id": provider.pk,
                    "professional_id": provider.professional_id,
                    "contact_phone": provider.contact_phone,
                    "contact_email": provider.contact_email,
                }
            except Provider.DoesNotExist:
                pass
        else:
            try:
                patient = user.patient
                patient_data = {
                    "id": patient.pk,
                    "contact_phone": patient.contact_phone,
                    "contact_email": patient.contact_email
                }
            except Patient.DoesNotExists:
                pass

        if patient_data:
            response = {
            "id": user.id,
            "email": user.email,
            "name": wounds_user.name or None,
            "birth_date": wounds_user.birth_date.isoformat() if wounds_user.birth_date else None,
            "state": wounds_user.state or None,
            "city": wounds_user.city or None,
            "role": _get_user_role_display(wounds_user),
            "registration_complete": _is_registration_complete(user),
            }

        return Response({
            "id": user.id,
            "email": user.email,
            "name": wounds_user.name or None,
            "birth_date": wounds_user.birth_date.isoformat() if wounds_user.birth_date else None,
            "state": wounds_user.state or None,
            "city": wounds_user.city or None,
            "role": _get_user_role_display(wounds_user),
            "registration_complete": _is_registration_complete(user),
            "specialist": specialist_data,
        })
