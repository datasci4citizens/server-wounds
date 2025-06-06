from .omop.omop_models import (
    Concept
)
from .omop import omop_ids
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

for const_name in all_attr_ofclass(omop_ids, int):
    try:
        Concept.objects.get_or_create(
            concept_id=  getattr(omop_ids, const_name),
            concept_name= const_name
        )
    except:
        pass

class VirtualSpecialistSerializer(VirtualModelSerializer):
    class Meta:
        super_model = VirtualSpecialist
        fields = "__all__"

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
        comorbidity_type = None
        if isinstance(obj, dict):
            comorbidity_type = obj.get('comorbidity_type')
        else:
            comorbidity_type = getattr(obj, 'comorbidity_type', None)
        if not comorbidity_type:
            return None
        concept = Concept.objects.filter(concept_id=comorbidity_type).first()
        return concept.concept_name if concept else None