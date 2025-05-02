from rest_framework import serializers, viewsets, routers, parsers

from django.urls import path, include
from .models import Specialists, Patients, Measurement, Comorbidities, Images, Wound, Observation, TrackingRecords
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from app_cicatrizando.google import google_get_user_data

from .models import *
# --- SERIALIZERS ---

class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialists
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = '__all__'

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = '__all__'

class ComorbiditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidities
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = '__all__'

class WoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wound
        fields = '__all__'

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = '__all__'

class TrackingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingRecords
        fields = '__all__'

# --- VIEWSETS ---


User = get_user_model()

# Just a test endpoint to check if the user is logged in and return user info
class MeView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )


class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    
class AuthTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    role = serializers.CharField()

class GoogleLoginView(viewsets.ViewSet):
    serializer_class = AuthSerializer
    permission_classes = [AllowAny]

    @extend_schema(request=AuthSerializer, responses={200: AuthTokenResponseSerializer})
    def create(self, request, *args, **kwargs):
        auth_serializer = self.serializer_class(data=request.data)
        auth_serializer.is_valid(raise_exception=True)

        validated_data = auth_serializer.validated_data

        # get user data from google
        user_data = google_get_user_data(validated_data)

        # Creates user in DB if first time login
        user, _ = User.objects.get_or_create(
            email=user_data.get("email"),
            username=user_data.get("email"),
            first_name=user_data.get("given_name"),
            last_name=user_data.get("given_name"),
        )

        role = "none"
        # if Specialists.objects.filter(user=user).exists():
        #     role = "specialist"
        # elif Patients.objects.filter(user=user).exists():
        #     role = "person"

        # generate jwt token for the user
        token = RefreshToken.for_user(user)
        response = {
            "access": str(token.access_token),
            "refresh": str(token),
            "role": role,
        }

        return Response(response, status=200)


class SpecialistViewSet(viewsets.ModelViewSet):
    queryset = Specialists.objects.all()
    serializer_class = SpecialistSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patients.objects.all()
    serializer_class = PatientSerializer

class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

class ComorbidityViewSet(viewsets.ModelViewSet):
    queryset = Comorbidities.objects.all()
    serializer_class = ComorbiditySerializer
AuthTokenResponseSerializer
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    parser_classes = [parsers.MultiPartParser]

class WoundViewSet(viewsets.ModelViewSet):
    queryset = Wound.objects.all()
    serializer_class = WoundSerializer

class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

class TrackingRecordViewSet(viewsets.ModelViewSet):
    queryset = TrackingRecords.objects.all()
    serializer_class = TrackingRecordSerializer

# --- ROUTER ---

router = routers.DefaultRouter()
router.register(r'specialists', SpecialistViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'measurements', MeasurementViewSet)
router.register(r'comorbidities', ComorbidityViewSet)
router.register(r'images', ImageViewSet)
router.register(r'wounds', WoundViewSet)
router.register(r'observations', ObservationViewSet)
router.register(r'tracking-records', TrackingRecordViewSet)
router.register(r'auth/google', GoogleLoginView, basename='google-login')
router.register(r'auth/me', MeView, basename='me')
# --- URLS ---

urlpatterns = [
    path('', include(router.urls)),
]
