from rest_framework import serializers

from .models import (
    Specialists, Patients, Comorbidities, 
    Images, Wound, TrackingRecords
)

class SpecialistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialists
        fields = '__all__'

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False



class ComorbiditiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidities
        fields = '__all__'
 


 

class PatientsSerializer(serializers.ModelSerializer): 
    specialist_id = serializers.PrimaryKeyRelatedField(
        queryset=Specialists.objects.all(),
        required =True
    )

    class Meta:
        model = Patients
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.allow_null = False

 


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
    wounds_id = WoundSerializer(read_only=True)
    specialist_id = SpecialistsSerializer(read_only=True)

    class Meta:
        model = TrackingRecords
        fields = '__all__'
