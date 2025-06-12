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
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Images
        fields = ['image_id', 'image', 'created_at', 'updated_at', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.field_name != 'image_url':  # Skip the new field
                field.required = True
                field.Allow_null = False


class WoundSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField instead of StringRelatedField for write operations
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patients.objects.all())
    specialist_id = serializers.PrimaryKeyRelatedField(queryset=Specialists.objects.all(), required=False, allow_null=True)
    image_id = serializers.PrimaryKeyRelatedField(queryset=Images.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Wound
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        # Only make essential fields required
        required_fields = ['patient_id', 'region', 'type', 'start_date']
        for field_name, field in self.fields.items():
            if field_name in required_fields:
                field.required = True
                field.allow_null = False
            else:
                field.required = False
                field.allow_null = True


class TrackingRecordsSerializer(serializers.ModelSerializer):
    image_id = serializers.PrimaryKeyRelatedField(queryset=Images.objects.all(), required=False, allow_null=True)
    wound_id = serializers.PrimaryKeyRelatedField(queryset=Wound.objects.all())
    specialist_id = serializers.PrimaryKeyRelatedField(queryset=Specialists.objects.all(), required=False, allow_null=True)

    class Meta:
        model = TrackingRecords
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ** kwargs)
        # Only make essential fields required
        required_fields = ['wound_id', 'length', 'width', 'track_date', 'exudate_amount', 'exudate_type', 'tissue_type']
        for field_name, field in self.fields.items():
            if field_name in required_fields:
                field.required = True
                field.allow_null = False
            else:
                field.required = False
                field.allow_null = True