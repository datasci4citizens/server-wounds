from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from datetime import date
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .firebase import firebase_get_user_data
from .models import WoundsUser, Provider, Patient
from .serializers import (
	FirebaseAuthSerializer,
	AuthTokenResponseSerializer,
	RoleSelectionSerializer,
	RoleSelectionResponseSerializer,
	ProviderProfileSerializer,
	PatientProfileSerializer,
	ProfileCompletionResponseSerializer,
)
import logging

logger = logging.getLogger("app_cicatrizando")

User = get_user_model()


def _has_field(model_cls, field_name):
	return any(field.name == field_name for field in model_cls._meta.fields)


def _relation_value(model_cls, relation_field_name, user, wounds_user):
	relation_field = model_cls._meta.get_field(relation_field_name)
	related_model = relation_field.remote_field.model
	if related_model == User:
		return user
	return wounds_user


def _get_or_create_wounds_user(user, selected_role):
	defaults = {}
	if _has_field(WoundsUser, "role"):
		defaults["role"] = selected_role
	if _has_field(WoundsUser, "birth_date"):
		defaults["birth_date"] = date(1900, 1, 1)

	return WoundsUser.objects.get_or_create(user=user, defaults=defaults)


def _serialize_wounds_user(wounds_user):
	data = {"id": wounds_user.pk}
	for field_name in ["role", "birth_date", "state", "city"]:
		if _has_field(WoundsUser, field_name):
			value = getattr(wounds_user, field_name)
			if hasattr(value, "isoformat"):
				value = value.isoformat()
			data[field_name] = value
	return data


def _apply_wounds_user_optional_updates(wounds_user, wounds_user_payload):
	updated_fields = []
	for field_name in ["birth_date", "state", "city"]:
		if field_name in wounds_user_payload and _has_field(WoundsUser, field_name):
			new_value = wounds_user_payload[field_name]
			if getattr(wounds_user, field_name) != new_value:
				setattr(wounds_user, field_name, new_value)
				updated_fields.append(field_name)

	if updated_fields:
		wounds_user.save(update_fields=updated_fields)

def _build_auth_response(validated_data, user_data):
	user_email = user_data.get("email")
	full_name = user_data.get("name") or f"{user_data.get('given_name', '')} {user_data.get('family_name', '')}".strip() or user_email

	user, created = User.objects.get_or_create(username=user_email, email=user_email)
	user_update_fields = []
	if user.email != user_email:
		user.email = user_email
		user_update_fields.append("email")
	if user_update_fields:
		user.save(update_fields=user_update_fields)

	selected_role = WoundsUser.Patient

	wounds_user, wounds_user_created = _get_or_create_wounds_user(user=user, selected_role=selected_role)

	if not wounds_user_created:
		update_fields = []
		if selected_role and (wounds_user.role != selected_role):
			wounds_user.role = selected_role
			update_fields.append("role")

		if _has_field(WoundsUser, "name") and full_name and (wounds_user.name != full_name):
			wounds_user.name = full_name
			update_fields.append("name")
		if _has_field(WoundsUser, "email") and (wounds_user.email != user_email):
			wounds_user.email = user_email
			update_fields.append("email")

		if update_fields:
			wounds_user.save(update_fields=update_fields)

	patient_data = None
	provider_data = None
	display_name = full_name
	if _has_field(WoundsUser, "name") and getattr(wounds_user, "name", None):
		display_name = wounds_user.name

	if wounds_user.role == WoundsUser.Provider:
		relation_field_name = "wounds_user" if _has_field(Provider, "wounds_user") else "WoundsUser"
		relation_value = _relation_value(Provider, relation_field_name, user, wounds_user)
		provider = Provider.objects.filter(**{relation_field_name: relation_value}).first()
		if provider:
			provider_data = {
				"provider_id": provider.pk,
				"provider_name": display_name,
			}
	else:
		relation_field_name = "WoundsUser" if _has_field(Patient, "WoundsUser") else "wounds_user"
		relation_value = _relation_value(Patient, relation_field_name, user, wounds_user)
		patient = Patient.objects.filter(**{relation_field_name: relation_value}).first()
		patient_data = {
			"patient_id": wounds_user.pk,
			"patient_name": display_name,
			"patient_profile_id": patient.pk if patient else None,
		}

	token = RefreshToken.for_user(user)

	role = "provider" if wounds_user.role == WoundsUser.Provider else "patient"
	profile_completion_required = created or wounds_user_created
	if wounds_user.role == WoundsUser.Provider and provider_data is None:
		profile_completion_required = True
	if wounds_user.role == WoundsUser.Patient and patient_data and patient_data.get("patient_profile_id") is None:
		profile_completion_required = True

	response = {
		"access": str(token.access_token),
		"refresh": str(token),
		"full_name": display_name,
		"email": user.email,
		"role": role,
		"is_new_user": created or wounds_user_created,
		"patient_data": patient_data,
		"provider_data": provider_data,
		"profile_completion_required": profile_completion_required,
	}
	return response


class MeView(viewsets.ViewSet):
	permission_classes = [IsAuthenticated]

	def list(self, request):
		user = request.user
		if user.is_anonymous:
			return Response({"message": "Não autenticado", "authenticated": False})

		wounds_user_name = None
		if hasattr(user, "wounds_user") and _has_field(WoundsUser, "name"):
			wounds_user_name = user.wounds_user.name

		return Response({
			"id": user.id,
			"username": user.username,
			"email": user.email,
			"name": wounds_user_name,
			"authenticated": True,
		})


class FirebaseLoginView(viewsets.ViewSet):
	serializer_class = FirebaseAuthSerializer
	permission_classes = [AllowAny]

	@extend_schema(request=FirebaseAuthSerializer, responses={200: AuthTokenResponseSerializer})
	def create(self, request, *args, **kwargs):
		logger.debug("Firebase login request")
		auth_serializer = self.serializer_class(data=request.data)
		auth_serializer.is_valid(raise_exception=True)
		validated_data = auth_serializer.validated_data

		user_data = firebase_get_user_data(validated_data["firebase_token"])
		logger.debug(f"User data from Firebase: {user_data}")

		response = _build_auth_response(validated_data=validated_data, user_data=user_data)
		return Response(response, status=200)


class RoleSelectionView(viewsets.ViewSet):
	serializer_class = RoleSelectionSerializer
	permission_classes = [IsAuthenticated]

	@extend_schema(request=RoleSelectionSerializer, responses={200: RoleSelectionResponseSerializer})
	def create(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		validated_data = serializer.validated_data
		selected_role = validated_data["role"]

		wounds_user, _ = _get_or_create_wounds_user(user=request.user, selected_role=selected_role)
		if wounds_user.role != selected_role:
			wounds_user.role = selected_role
			wounds_user.save(update_fields=["role"])

		profile_completion_required = True
		if selected_role == WoundsUser.Provider:
			relation_field_name = "wounds_user" if _has_field(Provider, "wounds_user") else "WoundsUser"
			relation_value = _relation_value(Provider, relation_field_name, request.user, wounds_user)
			profile_completion_required = Provider.objects.filter(**{relation_field_name: relation_value}).first() is None
		else:
			relation_field_name = "WoundsUser" if _has_field(Patient, "WoundsUser") else "wounds_user"
			relation_value = _relation_value(Patient, relation_field_name, request.user, wounds_user)
			profile_completion_required = Patient.objects.filter(**{relation_field_name: relation_value}).first() is None

		return Response(
			{
				"message": "Role selecionado com sucesso",
				"role": "provider" if selected_role == WoundsUser.Provider else "patient",
				"profile_completion_required": profile_completion_required,
			},
			status=200,
		)


class ProviderProfileView(viewsets.ViewSet):
	serializer_class = ProviderProfileSerializer
	permission_classes = [IsAuthenticated]

	@extend_schema(request=ProviderProfileSerializer, responses={200: ProfileCompletionResponseSerializer})
	def create(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		validated_data = serializer.validated_data

		wounds_user_payload = validated_data.get("wounds_user", {})
		provider_payload = validated_data.get("provider", {})

		wounds_user, _ = _get_or_create_wounds_user(user=request.user, selected_role=WoundsUser.Provider)
		if wounds_user.role != WoundsUser.Provider:
			return Response({"detail": "User role must be Pr to complete provider profile."}, status=400)

		_apply_wounds_user_optional_updates(wounds_user, wounds_user_payload)

		relation_field_name = "wounds_user" if _has_field(Provider, "wounds_user") else "WoundsUser"
		relation_value = _relation_value(Provider, relation_field_name, request.user, wounds_user)
		provider = Provider.objects.filter(**{relation_field_name: relation_value}).first()
		if provider is None:
			professional_id = provider_payload.get("professional_id")
			provider_create_data = {relation_field_name: relation_value}
			if _has_field(Provider, "Professional_ID"):
				provider_create_data["Professional_ID"] = professional_id
			if _has_field(Provider, "contact_email"):
				provider_create_data["contact_email"] = provider_payload.get("contact_email", "")
			if _has_field(Provider, "contact_number"):
				provider_create_data["contact_number"] = provider_payload.get("contact_number", "")
			provider = Provider.objects.create(**provider_create_data)

		provider_update_fields = []
		provider_field_map = {
			"professional_id": "Professional_ID",
			"contact_email": "contact_email",
			"contact_number": "contact_number",
		}
		for payload_key, model_field in provider_field_map.items():
			if payload_key in provider_payload and _has_field(Provider, model_field):
				new_value = provider_payload[payload_key]
				if getattr(provider, model_field) != new_value:
					setattr(provider, model_field, new_value)
					provider_update_fields.append(model_field)

		if provider_update_fields:
			provider.save(update_fields=provider_update_fields)

		provider_data = {
			"id": provider.pk,
			"professional_id": getattr(provider, "Professional_ID", None),
			"contact_email": getattr(provider, "contact_email", None),
			"contact_number": getattr(provider, "contact_number", None),
		}

		return Response(
			{
				"message": "Perfil provider atualizado com sucesso",
				"role": "provider",
				"wounds_user": _serialize_wounds_user(wounds_user),
				"provider": provider_data,
				"patient": None,
			},
			status=200,
		)


class PatientProfileView(viewsets.ViewSet):
	serializer_class = PatientProfileSerializer
	permission_classes = [IsAuthenticated]

	@extend_schema(request=PatientProfileSerializer, responses={200: ProfileCompletionResponseSerializer})
	def create(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		validated_data = serializer.validated_data

		wounds_user_payload = validated_data.get("wounds_user", {})
		patient_payload = validated_data.get("patient", {})

		selected_role = WoundsUser.Patient
		wounds_user, _ = _get_or_create_wounds_user(user=request.user, selected_role=selected_role)
		if wounds_user.role != WoundsUser.Patient:
			return Response({"detail": "User role must be Pa to complete patient profile."}, status=400)

		_apply_wounds_user_optional_updates(wounds_user, wounds_user_payload)

		relation_field_name = "WoundsUser" if _has_field(Patient, "WoundsUser") else "wounds_user"
		relation_value = _relation_value(Patient, relation_field_name, request.user, wounds_user)
		patient, _ = Patient.objects.get_or_create(**{relation_field_name: relation_value})

		patient_update_fields = []
		patient_field_map = {
			"contact_email": "contact_email",
			"contact_number": "contact_numer",
		}
		for payload_key, model_field in patient_field_map.items():
			if payload_key in patient_payload and _has_field(Patient, model_field):
				new_value = patient_payload[payload_key]
				if getattr(patient, model_field) != new_value:
					setattr(patient, model_field, new_value)
					patient_update_fields.append(model_field)

		if patient_update_fields:
			patient.save(update_fields=patient_update_fields)

		patient_data = {
			"id": patient.pk,
			"contact_email": getattr(patient, "contact_email", None),
			"contact_number": getattr(patient, "contact_numer", None),
		}

		return Response(
			{
				"message": "Perfil patient atualizado com sucesso",
				"role": "patient",
				"wounds_user": _serialize_wounds_user(wounds_user),
				"provider": None,
				"patient": patient_data,
			},
			status=200,
		)
