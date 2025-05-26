from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from .omop_models import Measurement, Observation, Person, Provider; 
from rest_framework import serializers
from django.db.models.fields import Field
from .virtual.models import CID_CENTIMETER, CID_DRINK_FREQUENCY, CID_HEIGHT, CID_KILOGRAM, CID_SMOKE_FREQUENCY, CID_WEIGHT, TableBinding, VirtualField, VirtualModel, FieldBind
from .virtual.serializers import VirtualModelSerializer
from rest_framework.routers import DefaultRouter

class TableBindings:
	class Observation(TableBinding):
		table = Observation
	class Measurement(TableBinding):
		table = Measurement
	class Person(TableBinding):
		table = Person
	class Provider(TableBinding):
		table = Provider

TableCreationOrder = [
	Provider, 
	Person,
	Measurement,
	Observation
]

class VirtualPatient(VirtualModel):
    patient_id = VirtualField(source=("person_row","person_id"))
    main_row = "person_row"
    person_row = TableBindings.Person(
        person_id 			 = FieldBind("patient_id", key = True),
        birth_datetime  	 = FieldBind("birthday"),
        year_of_birth        = FieldBind(0, const=True),
        race_concept_id      = FieldBind(0, const=True),
        ethnicity_concept_id = FieldBind(0, const=True),
        gender_concept_id	 = FieldBind("gender"),
        provider_id			 = FieldBind("specialist_id"),
        care_site_id		 = FieldBind("hospital_registration"),
        #name 				 = APIBind("name"), # não omop
        #email 				 = APIBind("email"), # não omop
        #phone_number 		 = APIBind("phone_number"), # não omop
        #accept_tcl 		 = APIBind("accept_tcl") # não omop
    )
    
    height_row = TableBindings.Measurement( 
        person_id 			= FieldBind("patient_id", key = True),
        value_as_number 	= FieldBind("height"),
        measurement_concept_id = FieldBind(CID_HEIGHT, const=True, key = True),
        unit_concept_id 	= FieldBind(CID_CENTIMETER, const=True),
        measurement_date 	= FieldBind("updated_at"),
        measurement_type_concept_id = FieldBind(0, const=True),
    )
    
    weight_row = TableBindings.Measurement(
        person_id 			= FieldBind("patient_id", key = True),
        value_as_number 	= FieldBind("weight"),
        measurement_concept_id = FieldBind(CID_WEIGHT, const=True, key = True),
        unit_concept_id	    = FieldBind(CID_KILOGRAM, const=True),
        measurement_date	= FieldBind("updated_at"),
        measurement_type_concept_id = FieldBind(0, const=True),
    )

    smoke_frequency = TableBindings.Observation(
        person_id 				= FieldBind("patient_id", key = True),
        observation_concept_id 	= FieldBind(CID_SMOKE_FREQUENCY, const=True, key = True),
        value_as_concept_id		= FieldBind("smoke_frequency"),
        observation_date 		= FieldBind("updated_at"),
        observation_type_concept_id = FieldBind(0, const=True),
    )

    drink_frequency = TableBindings.Observation(
        person_id 				= FieldBind("patient_id", key = True),
        observation_concept_id 	= FieldBind(CID_DRINK_FREQUENCY, const=True, key = True),
        value_as_concept_id 	= FieldBind("drink_frequency"),
        observation_date 		= FieldBind("updated_at"),
        observation_type_concept_id = FieldBind(0, const=True),
    )
print(VirtualPatient.descriptor().debug_str("Patient"))

class VirtualPatientSerializer(VirtualModelSerializer):
    class Meta:
        super_model = VirtualPatient
        model = VirtualPatient
        fields = "__all__"

class VirtualPatientViewSet(viewsets.ModelViewSet):
    queryset  = VirtualPatient.objects().all()
    serializer_class = VirtualPatientSerializer

class VirtualSpecialist(VirtualModel):
    main_row = "row_provider"
    row_provider = TableBindings.Provider(
        provider_id   = FieldBind("specialist_id", key = True),
        provider_name = FieldBind("specialist_name"),
        year_of_birth = FieldBind("birthday"),
        care_site_id   = FieldBind("site"),
        specialty_concept_id   = FieldBind("speciality")
    )
class VirtualSpecialistSerializer(VirtualModelSerializer):
    class Meta:
        super_model = VirtualSpecialist
        fields = "__all__"

class VirtualSpecialistViewSet(viewsets.ModelViewSet):
    queryset  = VirtualSpecialist.objects().all()
    serializer_class = VirtualSpecialistSerializer

router = DefaultRouter()
router.register(r'patients', VirtualPatientViewSet)
router.register(r'specialists', VirtualSpecialistViewSet)