from rest_framework import viewsets
from .omop_models import (
    Measurement, Observation, Person, Provider, 
    ConditionOccurrence, ProcedureOccurrence, Note, FactRelationship, Concept
)
from drf_spectacular.utils import extend_schema
from .omop_ids  import (
    CID_CENTIMETER, CID_DRINK_FREQUENCY, CID_HEIGHT, CID_KILOGRAM, CID_NULL, CID_SMOKE_FREQUENCY, 
    CID_WEIGHT, CID_WOUND_MANAGEMENT_NOTE, CID_WOUND_TYPE, CID_CONDITION_ACTIVE, CID_CONDITION_INACTIVE, CID_WOUND_LOCATION,
    CID_SURFACE_REGION, CID_WOUND_IMAGE, CID_UTF8, CID_PORTUGUESE, CID_PK_CONDITION_OCCURRENCE,
    CID_WOUND_PHOTOGRAPHY, CID_CONDITION_RELEVANT_TO, CID_PK_PROCEDURE_OCCURRENCE, CID_EXUDATE_AMOUNT,
    CID_EXUDATE_APPEARANCE, CID_WOUND_APPEARANCE, CID_WOUND_EDGE_DESCRIPTION, CID_WOUND_SKIN_AROUND,
    CID_FEVER, CID_NEGATIVE, CID_POSITIVE, CID_PAIN_SEVERITY, CID_DEGREE_FINDING, 
    CID_WOUND_CARE_DRESSING_CHANGE, CID_GENERIC_NOTE, CID_WOUND_LENGTH, CID_WOUND_WIDTH
)
from . import omop_ids
from .virtual.models import (
    TableBinding, VirtualField, VirtualModel, FieldBind, all_attr_ofclass
)
from .virtual.serializers import VirtualModelSerializer
from rest_framework.routers import DefaultRouter
from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatientViewSet)

for const_name in all_attr_ofclass(omop_ids, int):
    try:
        Concept.objects.get_or_create(
            concept_id=  getattr(omop_ids, const_name),
            concept_name= const_name
        )
        print(const_name, getattr(omop_ids, const_name))
    except:
        print("deu erro", const_name)

class VirtualSpecialistSerializer(VirtualModelSerializer):
    class Meta:
        super_model = VirtualSpecialist
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