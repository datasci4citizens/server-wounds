from rest_framework import serializers
from .models import Provider


# Valid Brazilian state codes
BRAZILIAN_STATES = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO"
]


def validate_brazilian_state(value):
    """Validate that the state is a valid 2-letter Brazilian state code."""
    value = value.upper()
    if value not in BRAZILIAN_STATES:
        raise serializers.ValidationError(
            f"Invalid Brazilian state code. Must be one of: {', '.join(BRAZILIAN_STATES)}"
        )
    else: 
        return value
    

# =============================================================================
# Request Serializers
# =============================================================================

class GoogleAuthSerializer(serializers.Serializer):
    """Request serializer for Google OAuth authentication."""
    auth_code = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    redirect_uri = serializers.CharField(required=False, default="postmessage", allow_blank=True)

class ProviderRegistrationSerializer(serializers.Serializer):
    """
    Request serializer for specialist registration.
    Flat structure for frontend simplicity.
    """
    # WoundsUser fields
    name = serializers.CharField(required=True, max_length=255)
    birth_date = serializers.DateField(required=True)
    state = serializers.CharField(required=True, max_length=2)
    city = serializers.CharField(required=True, max_length=100)
    
    # Provider/Specialist fields
    professional_id = serializers.CharField(required=True, max_length=50)
    contact_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    contact_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    def validate_state(self, value):
        return validate_brazilian_state(value)

class PatientRegisterSerializer(serializers.Serializer):
    "Request serializer for Patient registration"

    #User
    google_email = serializers.EmailField(required=True, max_length=50, allow_blank=False)

    # WoundsUser fields
    name = serializers.CharField(required=False, max_length=255)
    birth_date = serializers.DateField(required=False)
    state = serializers.CharField(required=False, max_length=2)
    city = serializers.CharField(required=False, max_length=100)

    # Patient fields
    contact_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    contact_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)


    def validate_state(self, value):
        return validate_brazilian_state(value)

class RegisterPatientComorbiditySerializer(serializers.Serializer):
    patient_id = serializers.CharField()
    patient_email = serializers.EmailField()
    comorbidities = serializers.ListField(child=serializers.CharField(max_length=220))


    def validate(self, data):
        if (not data.get("patient_id")) and (not data.get("patient_email")):
            raise serializers.ValidationError("at least one field is required")
        return data


# =============================================================================
# Response Serializers
# =============================================================================

class GoogleAuthResponseSerializer(serializers.Serializer):
    """Response serializer for Google OAuth authentication."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    registration_complete = serializers.BooleanField()
    role = serializers.CharField(allow_null=True)

class ProviderDataSerializer(serializers.Serializer):
    """Nested serializer for specialist-specific data."""

    id = serializers.IntegerField(required=True)
    professional_id = serializers.CharField(required=True)
    contact_phone = serializers.CharField(allow_blank=True, allow_null=True)
    contact_email = serializers.EmailField(allow_blank=True, allow_null=True)

class PatientDataSerializer(serializers.Serializer):
    """Nested serializer for patient-specific data."""

    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    contact_phone = serializers.CharField(allow_blank=True, allow_null=True)
    contact_email = serializers.EmailField(allow_blank=True, allow_null=True)
    assigned_specialists = serializers.ListField(required=False, default=list)
    comorbidities = serializers.ListField(required=False, default=list)

class UserDataSerializer(serializers.Serializer):
    """Nested serializer for wounds_user data."""
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    birth_date = serializers.DateField()
    state = serializers.CharField()
    city = serializers.CharField()
    role = serializers.CharField()

class ProviderRegisterResponseSerializer(serializers.Serializer):
    """Response serializer for specialist registration."""
    message = serializers.CharField()
    user = UserDataSerializer()
    specialist = ProviderDataSerializer()

class MeResponseSerializer(serializers.Serializer):
    """Response serializer for the /auth/me/ endpoint."""
    id = serializers.IntegerField(required =True)
    email = serializers.EmailField()
    name = serializers.CharField(allow_null=True)
    birth_date = serializers.DateField(allow_null=True)
    state = serializers.CharField(allow_null=True, allow_blank=True)
    city = serializers.CharField(allow_null=True, allow_blank=True)
    role = serializers.CharField(allow_null=True)
    registration_complete = serializers.BooleanField()
    specialist = ProviderDataSerializer(allow_null=True)
