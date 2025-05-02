from rest_framework import serializers, viewsets, routers, parsers

from django.urls import path, include
from .models import Specialists, Patients, Measurement, Comorbidities, Images, Wound, Observation, TrackingRecords

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

# --- URLS ---

urlpatterns = [
    path('', include(router.urls)),
]
