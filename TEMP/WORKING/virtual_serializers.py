from .omop.omop_models import (
    Concept
)
from .omop import omop_ids
from .omop.concept_loader import ensure_concepts_exist
from .django_virtualmodels.models import (
    all_attr_ofclass
)
from .django_virtualmodels.serializers import VirtualModelSerializer
from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient, VirtualComorbidity)
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import datetime
User = get_user_model()

# Load all concept IDs from omop_ids module
ensure_concepts_exist(omop_ids)

class VirtualSpecialistSerializer(serializers.Serializer):
    specialist_id   = serializers.IntegerField(read_only=True)
    specialist_name = serializers.CharField()
    email           = serializers.EmailField()
    birthday        = serializers.DateField(allow_null=True, required=False)
    speciality      = serializers.IntegerField(allow_null=True, required=False)
    city            = serializers.CharField(allow_null=True, required=False)
    state           = serializers.CharField(allow_null=True, required=False)

    @transaction.atomic()
    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"]
        )
        validated_data = VirtualSpecialist.create({
            "specialist_name": validated_data["specialist_name"],
            "user_id": user,  # Pass the user object directly, not just the ID
            "birthday": validated_data.get("birthday"),
            "speciality": validated_data.get("speciality"),
            "city": validated_data.get("city"),
            "state": validated_data.get("state"),
        })
        
        return {
            "specialist_id": validated_data["specialist_id"], 
            "specialist_name": validated_data["specialist_name"], 
            "email": user.email, 
            "birthday": validated_data["birthday"], 
            "speciality": validated_data["speciality"],
            "city": validated_data["city"],
            "state": validated_data["state"] 
        }

    def update(self, instance, validated_data : dict[str, object]):

        validated_data["specialist_id"] =  instance["provider_id"]
        updatable_fields = [
            "specialist_name",
            "birthday",
            "speciality",
            "city",
            "state"
        ]
        validated_data = VirtualSpecialist.update({
            field : validated_data[field]
            for field in updatable_fields
            if field in validated_data.keys()
        })
        return VirtualSpecialist.get(**validated_data)
class VirtualPatientSerializer(serializers.Serializer):
    patient_id            = serializers.IntegerField(read_only=True)
    name                  = serializers.CharField()
    gender                = serializers.IntegerField()
    birthday              = serializers.DateField()
    specialist_id         = serializers.IntegerField()
    hospital_registration = serializers.CharField()
    phone_number          = serializers.CharField()
    weight                = serializers.FloatField()
    height                = serializers.FloatField()
    accept_tcl            = serializers.BooleanField()
    smoke_frequency       = serializers.IntegerField(required=False)
    drink_frequency       = serializers.IntegerField(required=False)

    email                 = serializers.EmailField()
    comorbidities         = serializers.ListField(child=serializers.IntegerField(), allow_empty= True)
    comorbidities_to_add  = serializers.ListField(child=serializers.CharField(), allow_empty= True)
    @transaction.atomic()
    def create(self, validated_data):
        virtual_patient_fields  = [
            "name",
            "gender",
            "birthday",
            "specialist_id",
            "phone_number",
            "weight",
            "height",
            "accept_tcl",
            "smoke_frequency",
            "drink_frequency"
        ]
        data = {
            field: validated_data[field]
            for field in virtual_patient_fields
        }
        data["updated_at"] = datetime.now()
        validated_data = VirtualPatient.create(data)
        return {}  
class VirtualWoundSerializer(VirtualModelSerializer):
    class Meta:
        super_model = VirtualWound
        model = VirtualWound
        fields = "__all__"

class VirtualTrackingRecordsSerializer(VirtualModelSerializer):
    class Meta:
        super_model = VirtualTrackingRecords
        model = VirtualTrackingRecords
        fields = "__all__"
        
class VirtualComorbiditySerializer(VirtualModelSerializer):
    comorbidity_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        super_model = VirtualComorbidity
        model = VirtualComorbidity
        fields = "__all__"
        read_only_fields = ["comorbidity_id", "comorbidity_name"]

    def validate_comorbidity_type(self, value):
        # Garante que o concept existe
        if not Concept.objects.filter(concept_id=value).exists():
            raise serializers.ValidationError(f"O conceito com ID {value} não existe. Certifique-se de que ele foi criado.")
        return value

    def get_comorbidity_name(self, obj):
        # Suporta tanto dict quanto objeto
        comorbidity_type = None
        if isinstance(obj, dict):
            comorbidity_type = obj.get('comorbidity_type')
        else:
            comorbidity_type = getattr(obj, 'comorbidity_type', None)
        if not comorbidity_type:
            return None
        concept = Concept.objects.filter(concept_id=comorbidity_type).first()
        return concept.concept_name if concept else None