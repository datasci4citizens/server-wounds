from rest_framework import serializers
from .schema import Patients, Specialists, Wound, TrackingRecords, Observation, Comorbidities

class TrackingRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingRecords
        fields = '__all__'

class WoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wound
        fields = '__all__'

class ComorbiditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidities
        fields = '__all__'

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = '__all__'

class ObservationWithComorbiditiesSerializer(serializers.ModelSerializer):
    comorbidities = ComorbiditySerializer(many=True, read_only=True)
    
    class Meta:
        model = Observation
        fields = '__all__'

class PatientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = '__all__'

class SpecialistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialists
        fields = '__all__'

class WoundWithTrackingRecordsSerializer(serializers.ModelSerializer):
    tracking_records = TrackingRecordsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wound
        fields = '__all__'

class PatientsWithWoundsSerializer(serializers.ModelSerializer):
    wounds = WoundSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patients
        fields = '__all__'

class PatientsWithObservationsSerializer(serializers.ModelSerializer):
    observations = ObservationWithComorbiditiesSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patients
        fields = '__all__'

class SpecialistsWithPatientsSerializer(serializers.ModelSerializer):
    patients = PatientsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Specialists
        fields = '__all__'

class SpecialistsWithTrackingRecordsSerializer(serializers.ModelSerializer):
    tracking_records = TrackingRecordsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Specialists
        fields = '__all__'
