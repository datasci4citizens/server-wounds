from rest_framework import serializers

from .models import (
    Specialists, Patients, Comorbidities, PatientComorbidities,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False

class PatientComorbiditiesSerializer(serializers.ModelSerializer):
    patient = serializers.StringRelatedField()
    comorbidity = serializers.StringRelatedField()

    class Meta:
        model = PatientComorbidities
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False


class WoundSerializer(serializers.ModelSerializer):
    patient_id = serializers.StringRelatedField()
    specialist_id =  serializers.StringRelatedField() 
    image_id = serializers.StringRelatedField()

    class Meta:
        model = Wound
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False


class TrackingRecordsSerializer(serializers.ModelSerializer):
    image_id = serializers.StringRelatedField()
    wounds_id = serializers.StringRelatedField()
    specialist_id = serializers.StringRelatedField()

    class Meta:
        model = TrackingRecords
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False