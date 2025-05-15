from rest_framework import serializers

from .models import (
    Specialists, Patients, Comorbidities, PatientComorbidities,
    Images, Wound, TrackingRecords
)

class SpecialistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialists
        fields = '__all__'


class ComorbiditiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidities
        fields = '__all__'


class PatientComorbiditiesSerializer(serializers.ModelSerializer):
    patient = serializers.StringRelatedField()
    comorbidity = serializers.StringRelatedField()

    class Meta:
        model = PatientComorbidities
        fields = '__all__'


class PatientsSerializer(serializers.ModelSerializer): 
    specialist_id = SpecialistsSerializer(read_only=True)

    class Meta:
        model = Patients
        fields = '__all__'


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = '__all__'


class WoundSerializer(serializers.ModelSerializer):
    patient_id = PatientsSerializer(read_only=True)
    specialist_id = SpecialistsSerializer(read_only=True)
    image_id = ImagesSerializer(read_only=True)

    class Meta:
        model = Wound
        fields = '__all__'


class TrackingRecordsSerializer(serializers.ModelSerializer):
    image_id = ImagesSerializer(read_only=True)
    wound_id = WoundSerializer(read_only=True)
    specialist_id = SpecialistsSerializer(read_only=True)

    class Meta:
        model = TrackingRecords
        fields = '__all__'
