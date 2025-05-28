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
from .virtual_serializers import (VirtualSpecialistSerializer, VirtualWoundSerializer, VirtualTrackingRecordsSerializer)
from.virtual_views import(VirtualPatientViewSet, VirtualSpecialistViewSet, VirtualWoundViewSet, VirtualTrackingRecordsViewSet)

router = DefaultRouter()
router.register(r'virtual-patients', VirtualPatientViewSet)
router.register(r'virtual-specialists', VirtualSpecialistViewSet)
router.register(r'virtual-wounds', VirtualWoundViewSet)
router.register(r'virtual-tracking-records', VirtualTrackingRecordsViewSet)