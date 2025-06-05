from .omop.omop_models import (
    Concept
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
    birthday        = serializers.DateField(required=False)
    speciality      = serializers.IntegerField(required=False)
    city            = serializers.CharField(required=False)
    state           = serializers.CharField(required=False)

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
        print(*instance.__dict__.items())

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
class VirtualPatientSerializer(VirtualModelSerializer):
    class Meta:
        super_model = VirtualPatient
        model = VirtualPatient
        fields = "__all__"

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