from .omop.omop_models import (
    Concept,
    Observation
)
from .omop import omop_ids
from .django_virtualmodels.models import (
    all_attr_ofclass
)
from .django_virtualmodels.serializers import VirtualModelSerializer
from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient)
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import datetime
User = get_user_model()

for const_name in all_attr_ofclass(omop_ids, int):
    try:
        Concept.objects.get_or_create(
            concept_id=  getattr(omop_ids, const_name),
            concept_name= const_name
        )
    except:
        pass

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
            "user_id": user.id,
            "birthday": validated_data["birthday"],
            "speciality": validated_data["speciality"],
            "city": validated_data["city"],
            "state": validated_data["state"],
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
    specialist_id         = serializers.IntegerField(allow_null=True, required=False)
    hospital_registration = serializers.CharField(allow_null=True, required=False)
    phone_number          = serializers.CharField(allow_null=True, required=False)
    weight                = serializers.FloatField(allow_null=True, required=False)
    height                = serializers.FloatField(allow_null=True, required=False)
    accept_tcl            = serializers.BooleanField(required=False)
    smoke_frequency       = serializers.IntegerField(allow_null=True, required=False)
    drink_frequency       = serializers.IntegerField(allow_null=True, required=False)

    email                 = serializers.EmailField(read_only=True)
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
        
        result = VirtualPatient.create(data)
        
        print(result)
        for c in set(validated_data["comorbidities"]):
            obs = Observation.objects.create(
                person_id = result["patient_id"],
                observation_concept_id =  omop_ids.CID_COMORBIDITY,
                observation_type_concept_id = omop_ids.CID_EHR,
                value_as_concept_id = c,
                observation_date = data["updated_at"]
            )
        for c in set(validated_data["comorbidities_to_add"]):
            obs = Observation.objects.create(
                person_id = result["patient_id"],
                observation_concept_id =  omop_ids.CID_COMORBIDITY,
                observation_type_concept_id = omop_ids.CID_EHR,
                value_as_string = c,
                observation_date = data["updated_at"]
            )
        
        return result

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