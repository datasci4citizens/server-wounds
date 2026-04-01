from rest_framework import serializers


# Valid Brazilian state codes
BRAZILIAN_STATES = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO"
]


def validate_brazilian_state(value):
    """Validate that the state is a valid 2-letter Brazilian state code."""
    if value and value.upper() not in BRAZILIAN_STATES:
        raise serializers.ValidationError(
            f"Invalid Brazilian state code. Must be one of: {', '.join(BRAZILIAN_STATES)}"
        )
    return value.upper() if value else value


# =============================================================================
# Request Serializers
# =============================================================================

class GoogleAuthSerializer(serializers.Serializer):
    """Request serializer for Google OAuth authentication."""
    auth_code = serializers.CharField(required=True, allow_blank=False, allow_null=False)


class SpecialistRegistrationSerializer(serializers.Serializer):
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
    contact_phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    contact_email = serializers.EmailField(required=False, allow_blank=True)

    def validate_state(self, value):
        return validate_brazilian_state(value)


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


class SpecialistDataSerializer(serializers.Serializer):
    """Nested serializer for specialist-specific data."""
    id = serializers.IntegerField()
    professional_id = serializers.CharField()
    contact_phone = serializers.CharField(allow_blank=True)
    contact_email = serializers.EmailField(allow_blank=True)


class UserDataSerializer(serializers.Serializer):
    """Nested serializer for wounds_user data."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    birth_date = serializers.DateField()
    state = serializers.CharField()
    city = serializers.CharField()
    role = serializers.CharField()


class SpecialistRegistrationResponseSerializer(serializers.Serializer):
    """Response serializer for specialist registration."""
    message = serializers.CharField()
    user = UserDataSerializer()
    specialist = SpecialistDataSerializer()


class MeResponseSerializer(serializers.Serializer):
    """Response serializer for the /auth/me/ endpoint."""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField(allow_null=True)
    birth_date = serializers.DateField(allow_null=True)
    state = serializers.CharField(allow_null=True, allow_blank=True)
    city = serializers.CharField(allow_null=True, allow_blank=True)
    role = serializers.CharField(allow_null=True)
    registration_complete = serializers.BooleanField()
    specialist = SpecialistDataSerializer(allow_null=True)
