from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from .google import google_get_user_data
from .models import WoundsUser, Provider, Patient, Comorbidity
from django.db import transaction
from .serializers import (
    GoogleAuthSerializer,
    GoogleAuthResponseSerializer,
    ProviderRegistrationSerializer,
    ProviderRegisterResponseSerializer,
    PatientRegisterSerializer,
    PatientDataSerializer,
    RegisterPatientComorbiditySerializer,
    UpdateFieldsSerializer,
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
    - WoundsUser exists, with a role set and all information
    - If role is Provider, Provider record exists with professional_id
    - If role is Patient, Patient record exists, with at least one Provider
    """

    try:
        wounds_user = user.wounds_user
    except WoundsUser.DoesNotExist:
        return False

    if wounds_user.birth_date is None or wounds_user.state == "" or wounds_user.city == "":
        return False

    if wounds_user.role == WoundsUser.Provider:
        result = Provider.objects.filter(wounds_user=wounds_user, professional_id__isnull=False).exists()
    elif wounds_user.role == WoundsUser.Patient:
        result = Patient.objects.filter(wounds_user=wounds_user, assigned_providers__isnull=False).exists()
    else:
        result = False

    return result


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
                "contact_phone": data.get("contact_phone", None),
                "contact_email": data.get("contact_email", None),
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
                "birth_date": patient.wounds_user.birth_date,
                "state": patient.wounds_user.state,
                "city": patient.wounds_user.city,
                "contact_phone": patient.contact_phone,
                "contact_email": patient.contact_email,
                "gender": patient.gender,
                "height": patient.height,
                "weight": patient.weight,
                "smoking_status": patient.smoking_status,
                "alcohol_consumption": patient.alcohol_consumption,
                "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
            })
        
        return Response(response_data)

class SpecialistPatientUpdateView(viewsets.ViewSet):
    serializer = PatientRegisterSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Patient data retrieved successfully", response=PatientDataSerializer()),
            404: OpenApiResponse(description="Patient or Specialist not found")
        }
    )
    def retrieve(self, request, pk=None):
        user = request.user
        try:
            provider = user.wounds_user.provider
            patient = Patient.objects.get(pk=pk, assigned_providers=provider)
        except (WoundsUser.DoesNotExist, Provider.DoesNotExist):
            return Response("Specialist does not exist", status=status.HTTP_404_NOT_FOUND)
        except Patient.DoesNotExist:
            return Response("Patient not found or not assigned to this specialist", status=status.HTTP_404_NOT_FOUND)

        wounds_user = patient.wounds_user
        response = {
            "id": patient.id,
            "name": wounds_user.user.get_full_name(),
            "birth_date": wounds_user.birth_date,
            "state": wounds_user.state,
            "city": wounds_user.city,
            "contact_phone": patient.contact_phone,
            "contact_email": patient.contact_email,
            "gender": patient.gender,
            "height": patient.height,
            "weight": patient.weight,
            "smoking_status": patient.smoking_status,
            "alcohol_consumption": patient.alcohol_consumption,
            "assigned_specialists": [p.id for p in patient.assigned_providers.all()],
            "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
        }
        return Response(response, status=status.HTTP_200_OK)

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
        if "gender" in data:
            patient.gender = data["gender"]
        if "height" in data:
            patient.height = data["height"]
        if "weight" in data:
            patient.weight = data["weight"]
        if "smoking_status" in data:
            patient.smoking_status = data["smoking_status"]
        if "alcohol_consumption" in data:
            patient.alcohol_consumption = data["alcohol_consumption"]
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
            "birth_date": wounds_user.birth_date,
            "state": wounds_user.state,
            "city": wounds_user.city,
            "contact_phone": patient.contact_phone,
            "contact_email": patient.contact_email,
            "gender": patient.gender,
            "height": patient.height,
            "weight": patient.weight,
            "smoking_status": patient.smoking_status,
            "alcohol_consumption": patient.alcohol_consumption,
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

        
        name_in_list =  _split_full_name(data.get("name"))

        user_email = data["google_email"]
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

            # Update WoundsUser fields
            if "birth_date" in data: patient_wounds_user_object.birth_date = data["birth_date"]
            if "state" in data: patient_wounds_user_object.state = data["state"]
            if "city" in data: patient_wounds_user_object.city = data["city"]
            patient_wounds_user_object.save()

            response = {
                "id": patient.id,
                "name": data.get("name"),
                "birth_date": patient_wounds_user_object.birth_date,
                "state": patient_wounds_user_object.state,
                "city": patient_wounds_user_object.city,
                "contact_phone": patient.contact_phone,
                "contact_email": patient.contact_email,
                "gender": patient.gender,
                "height": patient.height,
                "weight": patient.weight,
                "smoking_status": patient.smoking_status,
                "alcohol_consumption": patient.alcohol_consumption,
                "assigned_specialists": [p.id for p in patient.assigned_providers.all()],
                "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
            }
            return Response(response, status=status.HTTP_200_OK)


        patient_wounds_user = WoundsUser.objects.create(
            user=patient_user,
            birth_date = data.get("birth_date", None),
            state = serializer.validate_state(data.get("state", "")),
            city = data.get("city", ""),
            role = WoundsUser.Patient,
        )

        patient, _ = Patient.objects.get_or_create(
            wounds_user=patient_wounds_user,
            defaults={
                "contact_phone": data.get("contact_phone") or None,
                "contact_email": data.get("contact_email") or None,
                "gender": data.get("gender") or None,
                "height": data.get("height") or None,
                "weight": data.get("weight") or None,
                "smoking_status": data.get("smoking_status") or None,
                "alcohol_consumption": data.get("alcohol_consumption") or [],
            }
        )
        
        patient.assigned_providers.add(provider)
        
        if "comorbidities" in data:
            comorbidities = Comorbidity.objects.filter(concept_id__in=data["comorbidities"])
            patient.comorbidities.set(comorbidities)

        response = {
          
            "id": patient.id,
            "name": data.get("name"),
            "birth_date": patient_wounds_user.birth_date,
            "state": patient_wounds_user.state,
            "city": patient_wounds_user.city,
            "contact_phone": patient.contact_phone,
            "contact_email": patient.contact_email,
            "gender": patient.gender,
            "height": patient.height,
            "weight": patient.weight,
            "smoking_status": patient.smoking_status,
            "alcohol_consumption": patient.alcohol_consumption,
            "assigned_specialists": [p.id for p in patient.assigned_providers.all()],
            "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
        }
        return Response(response, status=status.HTTP_201_CREATED)

class RegisterPatientComorbidityView(viewsets.ViewSet):
    serializer = RegisterPatientComorbiditySerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Comorbidities added successfully."),
            400: OpenApiResponse(description="Comorbidity not in Database."),
            403: OpenApiResponse(description="User is not allowed to add this patients comorbidity"),
            404: OpenApiResponse(description="Patient does not exist.")
        }
    )

    def create(self, request):
        request_user = request.user
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        

        try:
            if data.get("patient_id"):
                patient = Patient.objects.get(id=data.get("patient_id", None))
            elif data.get("patient_email"):
                target_user = User.objects.get(email=data.get("patient_email"))
                target_wounds_user = target_user.wounds_user
                patient = target_wounds_user.patient
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except (Patient.DoesNotExist, User.DoesNotExist, WoundsUser.DoesNotExist, AttributeError):
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        try:
            caller_wounds_user = request_user.wounds_user
        except WoundsUser.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if caller_wounds_user.role == WoundsUser.Provider:
            try:
                provider = caller_wounds_user.provider
            except Provider.DoesNotExist:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if not patient.assigned_providers.filter(pk=provider.pk).exists():
                return Response(status=status.HTTP_403_FORBIDDEN)
        elif caller_wounds_user != patient.wounds_user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        

        comorbidities_to_add = Comorbidity.objects.filter(concept_id__in=data.get('comorbidities', []))

        try:
            with transaction.atomic():
                patient.comorbidities.add(*comorbidities_to_add)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)

class UpdateFieldsView(viewsets.ViewSet):
    serializer = UpdateFieldsSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Information updated"),
            404: OpenApiResponse(description="User not found")
        }
    )
    def patch(self, request):
        user = request.user
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.get("name"):
            first, last = _split_full_name(data["name"])
            user.first_name, user.last_name = first, last
            user.save(update_fields=["first_name", "last_name"])

        try:
            wounds_user = user.wounds_user
        except WoundsUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if data.get("state") and (data["state"] != ""):
            wounds_user.state = data["state"]
        if data.get("city") and (data["city"] != ""):
            wounds_user.city = data["city"]
        if data.get("birth_date"):
            wounds_user.birth_date = data["birth_date"]

        wounds_user.save()

        if wounds_user.role == WoundsUser.Provider:
            provider = wounds_user.provider
            if data.get("contact_email") is not None:
                provider.contact_email = data["contact_email"]
            if data.get("contact_phone") is not None:
                provider.contact_phone = data["contact_phone"]
            provider.save()

        elif wounds_user.role == WoundsUser.Patient:
            patient = wounds_user.patient
            if data.get("contact_email") is not None:
                patient.contact_email = data["contact_email"]
            if data.get("contact_phone") is not None:
                patient.contact_phone = data["contact_phone"]
            
            # Update metrics
            if "gender" in data:
                patient.gender = data["gender"]
            if "height" in data:
                patient.height = data["height"]
            if "weight" in data:
                patient.weight = data["weight"]
            if "smoking_status" in data:
                patient.smoking_status = data["smoking_status"]
            if "alcohol_consumption" in data:
                patient.alcohol_consumption = data["alcohol_consumption"]
            
            # Update comorbidities
            if "comorbidities" in data:
                comorbidities = Comorbidity.objects.filter(concept_id__in=data["comorbidities"])
                patient.comorbidities.set(comorbidities)

            patient.save()

        return Response(status=status.HTTP_200_OK)

   
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
                "name": user.get_full_name(),
                "birth_date": wounds_user.birth_date,
                "state": wounds_user.state,
                "city": wounds_user.city,
                "contact_phone": patient.contact_phone,
                "contact_email": patient.contact_email,
                "gender": patient.gender,
                "height": patient.height,
                "weight": patient.weight,
                "smoking_status": patient.smoking_status,
                "alcohol_consumption": patient.alcohol_consumption,
                "assigned_specialists": [p.id for p in patient.assigned_providers.all()],
                "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
            }

        return Response(response)

class PatientMeView(viewsets.ViewSet):
    """
    GET authenticated patient's own health profile.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(response=PatientDataSerializer)
        }
    )
    def list(self, request):
        user = request.user
        try:
            wounds_user = user.wounds_user
            patient = wounds_user.patient
        except (WoundsUser.DoesNotExist, Patient.DoesNotExist):
            return Response("Patient profile not found", status=status.HTTP_404_NOT_FOUND)

        if wounds_user.role != WoundsUser.Patient:
            return Response("Access denied: Not a patient", status=status.HTTP_403_FORBIDDEN)

        response_data = {
            "id": patient.id,
            "name": user.get_full_name(),
            "birth_date": wounds_user.birth_date,
            "state": wounds_user.state,
            "city": wounds_user.city,
            "contact_phone": patient.contact_phone,
            "contact_email": patient.contact_email,
            "gender": patient.gender,
            "height": patient.height,
            "weight": patient.weight,
            "smoking_status": patient.smoking_status,
            "alcohol_consumption": patient.alcohol_consumption,
            "assigned_specialists": [
                {
                    "id": p.id,
                    "name": p.wounds_user.user.get_full_name(),
                    "professional_id": p.professional_id,
                    "contact_phone": p.contact_phone,
                    "contact_email": p.contact_email
                } for p in patient.assigned_providers.all()
            ],
            "comorbidities": ComorbiditySerializer(patient.comorbidities.all(), many=True).data
        }
        
        return Response(response_data)
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
        # Filter for "macro" diseases only: must have a code, and code must not contain a dot '.'
        queryset = queryset.filter(code__isnull=False).exclude(code__contains='.')
        
        search_query = self.request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(code__icontains=search_query))
        return queryset

from .serializers import WoundSerializer, ObservationSerializer
from .models import Wound, Observation
from rest_framework.decorators import action

class WoundViewSet(viewsets.ModelViewSet):
    """
    Manage patient wounds and their clinical observations.
    """
    queryset = Wound.objects.all()
    serializer_class = WoundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Wound.objects.all()
        user = self.request.user
        
        # Filter by patient_id if provided
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
            
        # Security: Patients only see their own wounds
        if hasattr(user, 'wounds_user') and user.wounds_user.role == WoundsUser.Patient:
            queryset = queryset.filter(patient__wounds_user=user.wounds_user)
        # Security: Specialists only see wounds of their assigned patients
        elif hasattr(user, 'wounds_user') and user.wounds_user.role == WoundsUser.Provider:
            queryset = queryset.filter(patient__assigned_providers=user.wounds_user.provider)
            
        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        # Only Specialists should create wounds
        if not hasattr(request.user, 'wounds_user') or request.user.wounds_user.role != WoundsUser.Provider:
            return Response({"error": "Only specialists can register new wounds."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['get', 'post'], url_path='observations')
    def observations(self, request, pk=None):
        wound = self.get_object()
        
        if request.method == 'GET':
            observations = wound.observations.all()
            serializer = ObservationSerializer(observations, many=True, context={'request': request})
            return Response(serializer.data)
        
        if request.method == 'POST':
            serializer = ObservationSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            # Link to wound and set current user as author
            serializer.save(wound=wound, author=request.user.wounds_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
