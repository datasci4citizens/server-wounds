from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from .google import google_get_user_data
from .models import WoundsUser, Provider, Patient, Comorbidity
from .serializers import (
    GoogleAuthSerializer,
    GoogleAuthResponseSerializer,
    ProviderRegistrationSerializer,
    ProviderRegisterResponseSerializer,
    PatientRegisterSerializer,
    PatientDataSerializer,
    RegisterPatientComobiditySerializer,
    MeResponseSerializer,
    ComorbiditySerializer,
)
import logging
logger = logging.getLogger(__name__)
User = get_user_model()


def _split_full_name(full_name: str):
    """Split full name into first_name and last_name for Django User."""
    parts = (full_name or "").strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])

def _user_display_name(user):
    """Return canonical display name from Django User."""
    full_name = user.get_full_name().strip()
    return full_name or None

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
        return Provider.objects.filter(wounds_user=wounds_user).exists()
    elif wounds_user.role == WoundsUser.Patient:
        return Patient.objects.filter(wounds_user=wounds_user).exists()

def _get_user_role_display(wounds_user:  WoundsUser) -> str: 
    """Convert role code to display string."""
    if not wounds_user or not wounds_user.role:
        return None
    return "specialist" if wounds_user.role == WoundsUser.Provider else "patient"

# Registration views
class GoogleLoginView(viewsets.ViewSet):
    """
    Google OAuth authentication endpoint.
    
    Exchanges Google auth code for JWT tokens.
    Returns 201 for new users, 200 for existing users.
    """
    serializer = GoogleAuthSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        request=GoogleAuthSerializer,
        responses={
            200: OpenApiResponse(response=GoogleAuthResponseSerializer),
            201: OpenApiResponse(response=GoogleAuthResponseSerializer),
        }
    )

    def create(self, request):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        google_user_data = google_get_user_data(data["auth_code"], data.get("redirect_uri", "postmessage"))
        logger.debug(f"User data from Google: {google_user_data}")

        user_given_email = google_user_data.get("email")
        full_name = (
            google_user_data.get("name") or
            f"{google_user_data.get('given_name', '')} {google_user_data.get('family_name', '')}".strip() or
            user_given_email.split('@')[0]
        )

        first_name, last_name = _split_full_name(full_name)
        
        user, new = User.objects.get_or_create(
            username=user_given_email,
        
            defaults={
                "first_name": first_name,
                "last_name" : last_name,
                "email": user_given_email
            }
        )
    
        wounds_user, wounds_user_created = WoundsUser.objects.get_or_create(
            user=user
        )

        is_new = new or wounds_user_created
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
    Complete provider registration.
    
    Sets user role to Specialist and creates professional profile.
    Requires JWT authentication.
    """
    serializer = ProviderRegistrationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProviderRegistrationSerializer,
        responses={
            200: OpenApiResponse(response=ProviderRegisterResponseSerializer),
            201: OpenApiResponse(response=ProviderRegisterResponseSerializer),
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Fills WoundsUser and Provider table
        """
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user

        wounds_user, _ = WoundsUser.objects.get_or_create(user=user)
        first_name, last_name = _split_full_name(data["name"])
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])
        
        wounds_user.birth_date = data["birth_date"]
        wounds_user.state = data["state"]
        wounds_user.city = data["city"]
        wounds_user.role = WoundsUser.Provider
        wounds_user.save()

        provider, _ = Provider.objects.update_or_create(
            wounds_user=wounds_user,
            defaults={
                "professional_id": data["professional_id"],
                "contact_phone": data.get("contact_phone") or None,
                "contact_email": data.get("contact_email") or None,
            }
        )

        response_data = {
            "message": "Specialist registered successfully",
            "user": {
                "id": wounds_user.pk,
                "name": _user_display_name(user),
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
            }
        }
    
        return Response(response_data, status=status.HTTP_201_CREATED)

# Functionality views

class SpecialistPatientListView(viewsets.ViewSet):
    """
        GET all patients related to a specific Provider/specialist
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(response=PatientDataSerializer(many=True)),
            404: OpenApiResponse(description="Specialist does not exist")
        }
    )
    def list(self, request):
        try:
            provider = request.user.wounds_user.provider

        except (WoundsUser.DoesNotExist, Provider.DoesNotExist, AttributeError):
            return Response("Specialist does not exist", status=status.HTTP_404_NOT_FOUND)

        patients = Patient.objects.filter(assigned_providers=provider)

        response_data = []
        for patient in patients:
            user_obj = patient.wounds_user.user
            name = user_obj.get_full_name()
            
            response_data.append({
                "id": patient.id,
                "name": name,
                "contact_phone": patient.contact_phone,
                "contact_email": patient.contact_email,
                "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
            })
        
        return Response(response_data)

class SpecialistPatientUpdateView(viewsets.ViewSet):
    serializer = PatientRegisterSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Patient updated successfully", response=PatientDataSerializer()),
            404: OpenApiResponse(description="Patient or Specialist not found")
        }
    )
    def update(self, request, pk=None):
        user = request.user
        try:
            provider = user.wounds_user.provider
            patient = Patient.objects.get(pk=pk, assigned_providers=provider)
        except (WoundsUser.DoesNotExist, Provider.DoesNotExist):
            return Response("Specialist does not exist", status=status.HTTP_404_NOT_FOUND)
        except Patient.DoesNotExist:
            return Response("Patient not found or not assigned to this specialist", status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Update patient fields
        if "contact_phone" in data:
            patient.contact_phone = data["contact_phone"]
        if "contact_email" in data:
            patient.contact_email = data["contact_email"]
        patient.save()

        # Update WoundsUser fields
        wounds_user = patient.wounds_user
        if "birth_date" in data:
            wounds_user.birth_date = data["birth_date"]
        if "state" in data:
            wounds_user.state = data["state"]
        if "city" in data:
            wounds_user.city = data["city"]
        wounds_user.save()

        # Update User fields (name)
        if "name" in data:
            name_in_list = _split_full_name(data["name"])
            django_user = wounds_user.user
            django_user.first_name = name_in_list[0]
            django_user.last_name = name_in_list[1]
            django_user.save()

        # Update Comorbidities
        if "comorbidities" in data:
            comorbidities = Comorbidity.objects.filter(concept_id__in=data["comorbidities"])
            patient.comorbidities.set(comorbidities)

        response = {
            "id": patient.id,
            "name": wounds_user.user.get_full_name() or data.get("name", ""),
            "contact_phone": patient.contact_phone,
            "contact_email": patient.contact_email,
            "assigned_specialists": [p.id for p in patient.assigned_providers.all()],
            "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
        }
        return Response(response, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

class SpecialistPatientRegisterView(viewsets.ViewSet):
    serializer = PatientRegisterSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Patient already exists, added specialist relation", response=PatientDataSerializer()),
            201: OpenApiResponse(description="Created new Patient entry", response=PatientDataSerializer()),
            404: OpenApiResponse(description="Specialist does not exist")
        }
    )

    def create(self, request):
        user = request.user
        try:
            provider = user.wounds_user.provider

        except (WoundsUser.DoesNotExist, Provider.DoesNotExist, AttributeError):
            return Response("Specialist does not exist", status=status.HTTP_404_NOT_FOUND)


        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        
        name_in_list =  _split_full_name(data["name"])

        user_email = data.get("google_email")
        patient_user, new = User.objects.get_or_create(
            username= user_email,
            defaults={
                "first_name" : name_in_list[0],
                "last_name" : name_in_list[1],
                "email": user_email
            }
        )

        if not new:
            patient_wounds_user_object = WoundsUser.objects.get(user=patient_user)
            patient = Patient.objects.get(wounds_user=patient_wounds_user_object)
            patient.assigned_providers.add(provider)

            if "comorbidities" in data:
                comorbidities = Comorbidity.objects.filter(concept_id__in=data["comorbidities"])
                patient.comorbidities.set(comorbidities)

            response = {
          
                "id": patient.id,
                "name": data.get("name"),
                "contact_phone": patient.contact_phone,
                "contact_email": patient.contact_email,
                "assigned_specialists": [p.id for p in patient.assigned_providers.all()],
                "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
            }
            return Response(response, status=status.HTTP_200_OK)
        

        patient_wounds_user = WoundsUser.objects.create(
            user=patient_user,
            birth_date = data.get("birth_date"),
            state = data.get("state", ""),
            city = data.get("city", ""),
            role = WoundsUser.Patient,
        )

        patient, _ = Patient.objects.get_or_create(
            wounds_user=patient_wounds_user,
            defaults={
                "contact_phone": data.get("contact_phone") or None,
                "contact_email": data.get("contact_email") or None,
            }
        )
        
        # Link to provider
        patient.assigned_providers.add(provider)
        
        if "comorbidities" in data:
            comorbidities = Comorbidity.objects.filter(concept_id__in=data["comorbidities"])
            patient.comorbidities.set(comorbidities)

        response = {
          
            "id": patient.id,
            "name": data.get("name"),
            "contact_phone": patient.contact_phone,
            "contact_email": patient.contact_email,
            "assigned_specialists": [p.id for p in patient.assigned_providers.all()],
            "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
        }
        return Response(response, status=status.HTTP_201_CREATED)

class RegisterPatientComobidityView(viewsets.ViewSet):
    serializer = RegisterPatientComobiditySerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(response=PatientDataSerializer)
        }
    )
    def create(self, request):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
    
        user = request.user
        Wounds = user.wounds_user
        patient = Wounds.patient

        for comorbidity in data.get('comorbidities', []):
          patient.comorbidities.add(comorbidity)

        return Response({"message": "Comorbidities added successfully"}, status=status.HTTP_200_OK)


class PatientValidationView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Patient exists and is allowed to login"),
            403: OpenApiResponse(description="Patient is not allowed to login")
        }

    )
    def list(self,request):
        user = request.user
        try:
            wounds_user_obj = WoundsUser.objects.get(user=user)
            patient_obj = Patient.objects.get(wounds_user=wounds_user_obj)
        except (WoundsUser.DoesNotExist, Patient.DoesNotExist):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        if wounds_user_obj.role == WoundsUser.Patient:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
class MeView(viewsets.ViewSet):
    """
    GET current user's complete profile.
    
    Returns user data including role-specific information.
    Requires JWT authentication.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(response=MeResponseSerializer)
        }
    )
    def list(self, request):
        user = request.user
        
        wounds_user = user.wounds_user

        response = {
            "id": user.id,
            "email": user.email,
            "name": _user_display_name(user),
            "birth_date": wounds_user.birth_date.isoformat() if wounds_user.birth_date else None,
            "state": wounds_user.state or None,
            "city": wounds_user.city or None,
            "role": _get_user_role_display(wounds_user),
            "registration_complete": _is_registration_complete(user),
        }
        
        if wounds_user.role == WoundsUser.Provider:
            provider = wounds_user.provider

            response["specialist"] = {
                "id": provider.id,
                "professional_id": provider.professional_id,
                "contact_phone": provider.contact_phone,
                "contact_email": provider.contact_email
            }

        elif wounds_user.role == WoundsUser.Patient:
            patient = wounds_user.patient

            response["patient"] = {
                "id": patient.id,
                "contact_phone": patient.contact_phone,
                "contact_email": patient.contact_email
            }

        return Response(response)
from rest_framework.pagination import LimitOffsetPagination

class ComorbidityPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

class ComorbiditySearchView(viewsets.ReadOnlyModelViewSet):
    queryset = Comorbidity.objects.all()
    serializer_class = ComorbiditySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ComorbidityPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(code__icontains=search_query))
        return queryset
