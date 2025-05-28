from rest_framework import viewsets
from .omop.omop_models import (
    Measurement, Observation, Person, Provider, 
    ConditionOccurrence, ProcedureOccurrence, Note, FactRelationship, Concept
)
from drf_spectacular.utils import extend_schema
from .omop.omop_ids  import (
    CID_CENTIMETER, CID_DRINK_FREQUENCY, CID_HEIGHT, CID_KILOGRAM, CID_NULL, CID_SMOKE_FREQUENCY, 
    CID_WEIGHT, CID_WOUND_MANAGEMENT_NOTE, CID_WOUND_TYPE, CID_CONDITION_ACTIVE, CID_CONDITION_INACTIVE, CID_WOUND_LOCATION,
    CID_SURFACE_REGION, CID_WOUND_IMAGE, CID_UTF8, CID_PORTUGUESE, CID_PK_CONDITION_OCCURRENCE,
    CID_WOUND_PHOTOGRAPHY, CID_CONDITION_RELEVANT_TO, CID_PK_PROCEDURE_OCCURRENCE, CID_EXUDATE_AMOUNT,
    CID_EXUDATE_APPEARANCE, CID_WOUND_APPEARANCE, CID_WOUND_EDGE_DESCRIPTION, CID_WOUND_SKIN_AROUND,
    CID_FEVER, CID_NEGATIVE, CID_POSITIVE, CID_PAIN_SEVERITY, CID_DEGREE_FINDING, 
    CID_WOUND_CARE_DRESSING_CHANGE, CID_GENERIC_NOTE, CID_WOUND_LENGTH, CID_WOUND_WIDTH
)
from .omop import omop_ids
from .django_virtualmodels.models import (
    TableBinding, VirtualField, VirtualModel, FieldBind
)
from .django_virtualmodels.serializers import VirtualModelSerializer
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
    class ConditionOccurrence(TableBinding):
        table = ConditionOccurrence
    class ProcedureOccurrence(TableBinding):
        table = ProcedureOccurrence
    class Note(TableBinding):
        table = Note
    class FactRelationship(TableBinding):
        table = FactRelationship

TableCreationOrder = [
    Provider,
    Person,
    ConditionOccurrence,
    ProcedureOccurrence,
    Measurement,
    Observation,
    Note,
    FactRelationship
]

class VirtualPatient(VirtualModel):
    patient_id = VirtualField(source=("person_row","person_id"), key=True)
    main_row = "person_row"
    person_row = TableBindings.Person(
        person_id            = FieldBind("patient_id", key = True),
        birth_datetime       = FieldBind("birthday"),
        year_of_birth        = FieldBind(CID_NULL, const=True),
        race_concept_id      = FieldBind(CID_NULL, const=True),
        ethnicity_concept_id = FieldBind(CID_NULL, const=True),
        gender_concept_id    = FieldBind("gender"),
        provider_id          = FieldBind("specialist_id"),
        care_site_id         = FieldBind("hospital_registration"),
        #name                = APIBind("name"), # não omop
        #phone_number        = APIBind("phone_number"), # não omop
        #accept_tcl          = APIBind("accept_tcl") # não omop
    )
    
    height_row = TableBindings.Measurement( 
        person_id              = FieldBind("patient_id", key = True),
        value_as_number        = FieldBind("height"),
        measurement_concept_id = FieldBind(CID_HEIGHT, const=True, key = True),
        unit_concept_id        = FieldBind(CID_CENTIMETER, const=True),
        measurement_date       = FieldBind("updated_at"),
        measurement_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    weight_row = TableBindings.Measurement(
        person_id              = FieldBind("patient_id", key = True),
        value_as_number        = FieldBind("weight"),
        measurement_concept_id = FieldBind(CID_WEIGHT, const=True, key = True),
        unit_concept_id        = FieldBind(CID_KILOGRAM, const=True),
        measurement_date       = FieldBind("updated_at"),
        measurement_type_concept_id = FieldBind(CID_NULL, const=True),
    )

    smoke_frequency = TableBindings.Observation(
        person_id                   = FieldBind("patient_id", key = True),
        observation_concept_id      = FieldBind(CID_SMOKE_FREQUENCY, const=True, key = True),
        value_as_concept_id         = FieldBind("smoke_frequency"),
        observation_date            = FieldBind("updated_at"),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )

    drink_frequency = TableBindings.Observation(
        person_id                   = FieldBind("patient_id", key = True),
        observation_concept_id      = FieldBind(CID_DRINK_FREQUENCY, const=True, key = True),
        value_as_concept_id         = FieldBind("drink_frequency"),
        observation_date            = FieldBind("updated_at"),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )


class VirtualSpecialist(VirtualModel):
    specialist_id = VirtualField(source=["row_provider", "provider_id"], key=True)
    main_row = "row_provider"
    row_provider = TableBindings.Provider(
        provider_id   = FieldBind("specialist_id", key = True),
        provider_name = FieldBind("specialist_name"),
        year_of_birth = FieldBind("birthday"),
        care_site_id   = FieldBind("site"),
        specialty_concept_id   = FieldBind("speciality")
    )
class VirtualWound(VirtualModel):
    wound_id = VirtualField(source=("condition_row", "condition_occurrence_id"), key=True)
    main_row = "condition_row"
    
    condition_row = TableBindings.ConditionOccurrence(
        condition_occurrence_id = FieldBind("wound_id", key=True),
        person_id = FieldBind("patient_id"),
        provider_id = FieldBind("specialist_id"),
        condition_concept_id = FieldBind(CID_WOUND_TYPE, const=True),
        condition_start_date = FieldBind("start_date"),
        condition_end_date = FieldBind("end_date"),
        condition_status_concept_id = FieldBind("is_active"),
        condition_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    observation_row = TableBindings.Observation(
        person_id = FieldBind("patient_id", key=True),
        observation_concept_id = FieldBind(CID_WOUND_LOCATION, const=True, key=True),
        observation_date = FieldBind("updated_at"),
        value_as_concept_id = FieldBind("region"),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
        observation_event_id = FieldBind("wound_id", key=True),
        obs_event_field_concept_id = FieldBind(CID_PK_CONDITION_OCCURRENCE, const=True),
    )
    
    note_row = TableBindings.Note(
        person_id = FieldBind("patient_id", key=True),
        note_date = FieldBind("updated_at"),
        note_class_concept_id = FieldBind(CID_WOUND_IMAGE, const=True, key=True),
        encoding_concept_id = FieldBind(CID_UTF8, const=True),
        language_concept_id = FieldBind(CID_PORTUGUESE, const=True),
        note_text = FieldBind("image_id"),
        note_event_id = FieldBind("wound_id", key=True),
        note_event_field_concept_id = FieldBind(CID_PK_CONDITION_OCCURRENCE, const=True),
        note_type_concept_id = FieldBind(CID_NULL, const=True),

    )


def _tr_measurement(**kwargs):
    return TableBindings.Measurement(
        person_id = FieldBind("patient_id", key=True),
        measurement_date = FieldBind("updated_at"),
        measurement_event_id = FieldBind("tracking_id", key=True),
        meas_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        measurement_type_concept_id = FieldBind(CID_NULL, const=True),
        **kwargs
    )
def _tr_measurement_value_cid(virtual: str, concept: int):
    return _tr_measurement(
        value_as_concept_id = FieldBind(virtual),   
        measurement_concept_id = FieldBind(concept, const = True)
    )    

def _tr_measurement_value_number(virtual: str, concept: int, cid_unit : int):
    return _tr_measurement(
        value_as_number = FieldBind(virtual),   
        measurement_concept_id = FieldBind(concept, const = True),
        unit_concept_id = FieldBind(cid_unit, const = True)
    )    
class VirtualTrackingRecords(VirtualModel):
    tracking_id = VirtualField(source=("procedure_row", "procedure_occurrence_id"), key=True)
    main_row = "procedure_row"
    
    procedure_row = TableBindings.ProcedureOccurrence(
        procedure_occurrence_id = FieldBind("tracking_id", key=True),
        person_id = FieldBind("patient_id", key=True),
        provider_id = FieldBind("specialist_id", key=True),
        procedure_concept_id = FieldBind(CID_WOUND_PHOTOGRAPHY, const=True),
        procedure_date = FieldBind("track_date"),
        procedure_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    fact_relation_row = TableBindings.FactRelationship(
        domain_concept_id_1_id = FieldBind(CID_PK_CONDITION_OCCURRENCE, const=True),
        fact_id_1 = FieldBind("wound_id"),
        relationship_concept_id = FieldBind(CID_CONDITION_RELEVANT_TO, const=True, key=True),
        domain_concept_id_2_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        fact_id_2 = FieldBind("tracking_id", key=True),
    )
    
    # Measurements
    length_measurement = _tr_measurement_value_number("length", CID_WOUND_LENGTH, CID_CENTIMETER),
    width_measurement  = _tr_measurement_value_number("width", CID_WOUND_WIDTH, CID_CENTIMETER)
    
    exudate_amount_measurement  = _tr_measurement_value_cid("exudate_amount", CID_EXUDATE_AMOUNT)
    exudate_type_measurement    = _tr_measurement_value_cid("exudate_type", CID_EXUDATE_APPEARANCE)    
    tissue_type_measurement     = _tr_measurement_value_cid("tissue_type", CID_WOUND_APPEARANCE)
    wound_edges_measurement     = _tr_measurement_value_cid("wound_edges", CID_WOUND_EDGE_DESCRIPTION)
    skin_around_measurement     = _tr_measurement_value_cid("skin_around", CID_WOUND_SKIN_AROUND)
    had_a_fever_measurement     = _tr_measurement_value_cid("had_a_fever", CID_FEVER)
    pain_level_measurement      = _tr_measurement_value_cid("pain_level", CID_PAIN_SEVERITY)
    dressing_changes_per_day_measurement = _tr_measurement_value_cid("dressing_changes_per_day", CID_WOUND_CARE_DRESSING_CHANGE)

    # Notes
    image_note = TableBindings.Note(
        person_id = FieldBind("patient_id"),
        note_date = FieldBind("updated_at"),
        note_class_concept_id = FieldBind(CID_WOUND_IMAGE, const=True),
        encoding_concept_id = FieldBind(CID_UTF8, const=True),
        language_concept_id = FieldBind(CID_PORTUGUESE, const=True),
        note_text = FieldBind("image_id"),
        note_event_id = FieldBind("tracking_id", key=True),
        note_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        note_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    guidelines_note = TableBindings.Note(
        person_id = FieldBind("patient_id"),
        note_date = FieldBind("updated_at"),
        note_class_concept_id = FieldBind(CID_WOUND_MANAGEMENT_NOTE, const=True, key = True),
        encoding_concept_id = FieldBind(CID_UTF8, const=True),
        language_concept_id = FieldBind(CID_PORTUGUESE, const=True),
        note_text = FieldBind("guidelines_to_patient"),
        note_event_id = FieldBind("tracking_id", key=True),
        note_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        note_type_concept_id = FieldBind(CID_NULL, const=True),
    )

    extra_notes_note = TableBindings.Note(
        person_id = FieldBind("patient_id"),
        note_date = FieldBind("updated_at"),
        note_class_concept_id = FieldBind(CID_GENERIC_NOTE, const=True, key = True),
        encoding_concept_id = FieldBind(CID_UTF8, const=True),
        language_concept_id = FieldBind(CID_PORTUGUESE, const=True),
        note_text = FieldBind("extra_notes"),
        note_event_id = FieldBind("tracking_id", key=True),
        note_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        note_type_concept_id = FieldBind(CID_NULL, const=True),
    )
