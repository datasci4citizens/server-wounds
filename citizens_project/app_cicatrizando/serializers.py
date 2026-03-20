from rest_framework import serializers
from .models import WoundsUser


class FirebaseAuthSerializer(serializers.Serializer):
	firebase_token = serializers.CharField(required=True, allow_blank=False, allow_null=False)


class RoleSelectionSerializer(serializers.Serializer):
	role = serializers.ChoiceField(choices=[WoundsUser.Provider, WoundsUser.Patient])


class AuthTokenResponseSerializer(serializers.Serializer):
	access = serializers.CharField()
	refresh = serializers.CharField()
	full_name = serializers.CharField()
	email = serializers.EmailField()
	role = serializers.CharField()
	is_new_user = serializers.BooleanField()
	patient_data = serializers.DictField(allow_null=True)
	provider_data = serializers.DictField(allow_null=True)
	profile_completion_required = serializers.BooleanField()


class WoundsUserCompletionSerializer(serializers.Serializer):
	birth_date = serializers.DateField(required=False)
	state = serializers.CharField(required=False, allow_blank=True)
	city = serializers.CharField(required=False, allow_blank=True)


class ProviderCompletionSerializer(serializers.Serializer):
	professional_id = serializers.IntegerField(required=False, min_value=1)
	contact_email = serializers.EmailField(required=False, allow_blank=True)
	contact_number = serializers.CharField(required=False, allow_blank=True)


class PatientCompletionSerializer(serializers.Serializer):
	contact_email = serializers.EmailField(required=False, allow_blank=True)
	contact_number = serializers.CharField(required=False, allow_blank=True)


class ProviderProfileSerializer(serializers.Serializer):
	wounds_user = WoundsUserCompletionSerializer(required=False)
	provider = ProviderCompletionSerializer(required=True)

	def validate(self, attrs):
		provider_payload = attrs.get("provider")
		if provider_payload and provider_payload.get("professional_id") is None:
			raise serializers.ValidationError({"provider": "professional_id is required."})
		return attrs


class PatientProfileSerializer(serializers.Serializer):
	wounds_user = WoundsUserCompletionSerializer(required=False)
	patient = PatientCompletionSerializer(required=False)


class ProfileCompletionResponseSerializer(serializers.Serializer):
	message = serializers.CharField()
	role = serializers.CharField()
	wounds_user = serializers.DictField(allow_null=True)
	provider = serializers.DictField(allow_null=True)
	patient = serializers.DictField(allow_null=True)


class RoleSelectionResponseSerializer(serializers.Serializer):
	message = serializers.CharField()
	role = serializers.CharField()
	profile_completion_required = serializers.BooleanField()
