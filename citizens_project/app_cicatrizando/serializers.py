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
 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False

<<<<<<< HEAD
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

=======
 
>>>>>>> c5bd38ecdd473b8af096504908a9a611897982ad

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

<<<<<<< HEAD
=======
 
>>>>>>> c5bd38ecdd473b8af096504908a9a611897982ad


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
<<<<<<< HEAD
    patient_id = serializers.StringRelatedField()
    specialist_id =  serializers.StringRelatedField() 
    image_id = serializers.StringRelatedField()
=======
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patients.objects.all())
    specialist_id = serializers.PrimaryKeyRelatedField(queryset=Specialists.objects.all())
    image_id = serializers.PrimaryKeyRelatedField(queryset=Images.objects.all())
>>>>>>> c5bd38ecdd473b8af096504908a9a611897982ad

    class Meta:
        model = Wound
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False


class TrackingRecordsSerializer(serializers.ModelSerializer):
<<<<<<< HEAD
    image_id = serializers.StringRelatedField()
    wounds_id = serializers.StringRelatedField()
    specialist_id = serializers.StringRelatedField()
=======
    image_id = ImagesSerializer(read_only=True)
    wounds_id = WoundSerializer(read_only=True)
    specialist_id = SpecialistsSerializer(read_only=True)
>>>>>>> c5bd38ecdd473b8af096504908a9a611897982ad

    class Meta:
        model = TrackingRecords
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        for field in self.fields.values():
            field.required = True
            field.Allow_null = False