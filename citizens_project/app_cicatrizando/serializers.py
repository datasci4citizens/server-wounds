from rest_framework import serializers
from .models import WoundsUser


class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_null=False, allow_blank=False)
    token = serializers.CharField(required=False, allow_null=False, allow_blank=False)
    birth_date = serializers.DateField(required=False)
    role = serializers.ChoiceField(
        choices=[WoundsUser.Provider, WoundsUser.Patient],
        required=False,
        default=WoundsUser.Patient,
    )


class AuthTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    role = serializers.CharField()
    is_new_user = serializers.BooleanField()
    patient_data = serializers.DictField(allow_null=True)
    provider_data = serializers.DictField(allow_null=True)
    profile_completion_required = serializers.BooleanField()
