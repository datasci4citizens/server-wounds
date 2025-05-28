from .omop_models import (
    Concept
)
from . import omop_ids
from .virtual.models import (
    all_attr_ofclass
)
from .virtual.serializers import VirtualModelSerializer
from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient)

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