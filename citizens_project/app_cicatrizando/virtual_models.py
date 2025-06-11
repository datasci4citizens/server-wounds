import datetime
from rest_framework import viewsets

from .models import PatientNonClinicalInfos, Image, TrackingRecordImage, WoundImage
from .omop.omop_models import (
    Location, Measurement, Observation, Person, Provider, 
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
    CID_WOUND_CARE_DRESSING_CHANGE, CID_GENERIC_NOTE, CID_WOUND_LENGTH, CID_WOUND_WIDTH, CID_COMORBIDITY
)
from .omop import omop_ids
from .django_virtualmodels.models import (
    ChoiceMap, TableBinding, VirtualField, VirtualModel, FieldBind
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
    class PatientNonClinicalInfos(TableBinding):
        table = PatientNonClinicalInfos
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
    class Location(TableBinding):
        table = Location
    class TrackingRecordImage(TableBinding):
        table = TrackingRecordImage
    class WoundImage(TableBinding):
        table = WoundImage


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



map_gender = ChoiceMap([
    ("female", omop_ids.CID_FEMALE),
    ("male", omop_ids.CID_MALE)
])
map_smoke_frequency = ChoiceMap([
  ("0", omop_ids.CID_NEVER),
  ("1", omop_ids.CID_OCCASIONALLY),
  ("2", omop_ids.CID_10_OR_LESS),
  ("3", omop_ids.CID_10_OR_MORE)
])

map_drink_frequency = ChoiceMap([
    ("0", omop_ids.CID_DRINK_NEVER),
    ("1", omop_ids.CID_DRINK_MONTHLY_OR_LESS),
    ("2", omop_ids.CID_DRINK_2_3_TIMES_WEEK),
    ("3", omop_ids.CID_DRINK_4_OR_MORE_WEEK),
])
map_comorbidities = ChoiceMap([   
  ("5A10", omop_ids.CID_DIABETES),
  ("5A11", omop_ids.CID_DIABETES2),
  ("BA00", omop_ids.CID_HIPERTENSAO),
  ("5B81", omop_ids.CID_OBESIDADE),
  ("8B20", omop_ids.CID_DPOC), # TODO VERIFICAR DEPOIS
  ("5C80", omop_ids.CID_DOENCA_RENAL_CRONICA )# TODO VERIFICAR DEPOIS,
])

class VirtualPatient(VirtualModel):
    patient_id = VirtualField(source=("row_person","person_id"), key=True)
    name                  = VirtualField(source=("row_nonclinicalinfos", "name"))
    gender                = VirtualField(source=("row_person", "gender_concept_id"), choicemap=map_gender)
    birthday              = VirtualField(source=("row_person", "birth_datetime"))
    specialist_id         = VirtualField(source=("row_person", "provider_id"))
    hospital_registration = VirtualField(source=("row_person", "person_care_site_registration"))
    phone_number          = VirtualField(source=("row_nonclinicalinfos", "phone_number"))
    weight                = VirtualField(source=("row_weight", "value_as_number"))
    height                = VirtualField(source=("row_height", "value_as_number"))
    accept_tcl            = VirtualField(source=("row_nonclinicalinfos", "accept_tcl"))
    smoke_frequency       = VirtualField(source=("row_smoke_frequency", "value_as_concept_id"), choicemap=map_smoke_frequency)
    drink_frequency       = VirtualField(source=("row_drink_frequency", "value_as_concept_id"), choicemap=map_drink_frequency)
    user_id               = VirtualField(source=("row_person", "person_user_id"))
    updated_at            = VirtualField(source=("row_height", "measurement_date"))
    main_row = "row_person"
    row_person = TableBindings.Person(
        person_id                     = FieldBind("patient_id", key = True),
        birth_datetime                = FieldBind("birthday"),
        year_of_birth                 = FieldBind(CID_NULL, const=True),
        race_concept_id               = FieldBind(CID_NULL, const=True),
        ethnicity_concept_id          = FieldBind(CID_NULL, const=True),
        gender_concept_id             = FieldBind("gender"),
        provider_id                   = FieldBind("specialist_id"),
        person_care_site_registration = FieldBind("hospital_registration"),
        person_user_id                = FieldBind("user_id")
    )
    row_nonclinicalinfos = TableBindings.PatientNonClinicalInfos(
        person_id    = FieldBind("patient_id"),
        name         = FieldBind("name"),
        phone_number = FieldBind("phone_number"),
        accept_tcl   = FieldBind("accept_tcl"),
    )
    
    row_height = TableBindings.Measurement( 
        person_id              = FieldBind("patient_id", key = True),
        value_as_number        = FieldBind("height"),
        measurement_concept_id = FieldBind(CID_HEIGHT, const=True, key = True),
        unit_concept_id        = FieldBind(CID_CENTIMETER, const=True),
        measurement_date       = FieldBind("updated_at"),
        measurement_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    row_weight = TableBindings.Measurement(
        person_id              = FieldBind("patient_id", key = True),
        value_as_number        = FieldBind("weight"),
        measurement_concept_id = FieldBind(CID_WEIGHT, const=True, key = True),
        unit_concept_id        = FieldBind(CID_KILOGRAM, const=True),
        measurement_date       = FieldBind("updated_at"),
        measurement_type_concept_id = FieldBind(CID_NULL, const=True),
    )

    row_smoke_frequency = TableBindings.Observation(
        person_id                   = FieldBind("patient_id", key = True),
        observation_concept_id      = FieldBind(CID_SMOKE_FREQUENCY, const=True, key = True),
        value_as_concept_id         = FieldBind("smoke_frequency"),
        observation_date            = FieldBind("updated_at"),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )

    row_drink_frequency = TableBindings.Observation(
        person_id                   = FieldBind("patient_id", key = True),
        observation_concept_id      = FieldBind(CID_DRINK_FREQUENCY, const=True, key = True),
        value_as_concept_id         = FieldBind("drink_frequency"),
        observation_date            = FieldBind("updated_at"),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    @classmethod
    def get_comorbidities(cls, patient_id : int):
        queryset = Observation.objects.all().filter(person_id=patient_id, observation_concept_id=omop_ids.CID_COMORBIDITY)
        comorbidities = []
        for c in queryset:
            comorbidities.append(map_comorbidities.db_to_virtual(c.value_as_concept_id))
            
        return comorbidities
class VirtualSpecialist(VirtualModel):
    specialist_id   = VirtualField(source=("row_provider", "provider_id"), key=True)
    specialist_name = VirtualField(source=("row_provider", "provider_name"))
    user_id         = VirtualField(source=("row_provider", "provider_user_id")), 
    birthday        = VirtualField(source=("row_provider", "provider_birthday"), null=True)
    speciality      = VirtualField(source=("row_provider", "specialty_string"), null=True)
    city            = VirtualField(source=("row_location", "city"), null=True)
    state           = VirtualField(source=("row_location", "state"), null=True)
    main_row = "row_provider"
    row_provider = TableBindings.Provider(
        provider_id       = FieldBind("specialist_id", key = True),
        provider_name     = FieldBind("specialist_name"),
        provider_birthday = FieldBind("birthday"),
        provider_user_id  = FieldBind("user_id"),
        specialty_string  = FieldBind("speciality")
    )

    row_location =  TableBindings.Location(
        location_id = FieldBind("specialist_id", key=True),
        city        = FieldBind("city"),  
        state       = FieldBind("state"),  
    )

class VirtualWound(VirtualModel):
    wound_id      = VirtualField(source=("row_condition", "condition_occurrence_id"), key=True)
    region        = VirtualField(source=("row_region", "value_as_concept_id"))
    wound_type    = VirtualField(source=("row_condition", "condition_concept_id")) 
    start_date    = VirtualField(source=("row_condition", "condition_start_date"))
    end_date      = VirtualField(source=("row_condition", "condition_end_date"))
    is_active     = VirtualField(source=("row_condition", "condition_status_concept_id"))
    image_id      = VirtualField(source=("row_image", "image_id"), null=True)
    patient_id    = VirtualField(source=("row_condition", "person_id"))
    specialist_id = VirtualField(source=("row_condition", "provider_id"))
    updated_at    = VirtualField(source=("row_region", "observation_date"))
    main_row = "row_condition"
    row_condition = TableBindings.ConditionOccurrence(
        condition_occurrence_id = FieldBind("wound_id", key=True),
        person_id                   = FieldBind("patient_id"),
        provider_id                 = FieldBind("specialist_id"),
        condition_concept_id        = FieldBind("wound_type"),
        condition_start_date        = FieldBind("start_date"),
        condition_end_date          = FieldBind("end_date"),
        condition_status_concept_id = FieldBind("is_active"),
        condition_type_concept_id   = FieldBind(CID_NULL, const=True),
    )
    
    row_region = TableBindings.Observation(
        person_id                   = FieldBind("patient_id", key=True),
        observation_concept_id      = FieldBind(CID_WOUND_LOCATION, const=True, key=True),
        observation_date            = FieldBind("updated_at"),
        value_as_concept_id         = FieldBind("region"),
        observation_event_id        = FieldBind("wound_id", key=True),
        obs_event_field_concept_id  = FieldBind(CID_PK_CONDITION_OCCURRENCE, const=True),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    row_image = TableBindings.WoundImage(
        image_id = FieldBind("image_id"),
        wound_id = FieldBind("wound_id", key=True),
    )
    # row_note_image = TableBindings.Note(
    #     person_id                   = FieldBind("patient_id", key=True),
    #     note_date                   = FieldBind("updated_at"),
    #     note_class_concept_id       = FieldBind(CID_WOUND_IMAGE, const=True, key=True),
    #     encoding_concept_id         = FieldBind(CID_UTF8, const=True),
    #     language_concept_id         = FieldBind(CID_PORTUGUESE, const=True),
    #     note_text                   = FieldBind("image_id"),
    #     note_event_id               = FieldBind("wound_id", key=True),
    #     note_event_field_concept_id = FieldBind(CID_PK_CONDITION_OCCURRENCE, const=True),
    #     note_type_concept_id        = FieldBind(CID_NULL, const=True),
    # )


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
    tracking_id              = VirtualField(source=("row_procedure", "procedure_occurrence_id"), key=True)
    patient_id               = VirtualField(source=("row_procedure", "person_id"))
    specialist_id            = VirtualField(source=("row_procedure", "provider_id"))
    track_date               = VirtualField(source=("row_procedure", "procedure_date"))
    wound_id                 = VirtualField(source=("row_fact_relation", "fact_id_1"))
    updated_at               = VirtualField(source=("row_length", "measurement_date"))
    length                   = VirtualField(source=("row_length", "value_as_number"))
    width                    = VirtualField(source=("row_width", "value_as_number"))
    exudate_amount           = VirtualField(source=("row_exudate_amount", "value_as_concept_id"))
    exudate_type             = VirtualField(source=("row_exudate_type", "value_as_concept_id"))
    tissue_type              = VirtualField(source=("row_tissue_type", "value_as_concept_id"))
    wound_edges              = VirtualField(source=("row_wound_edges", "value_as_concept_id"))
    skin_around              = VirtualField(source=("row_skin_around", "value_as_concept_id"))
    had_a_fever              = VirtualField(source=("row_had_a_fever", "value_as_concept_id"))
    pain_level               = VirtualField(source=("row_pain_level", "value_as_concept_id"))
    dressing_changes_per_day = VirtualField(source=("row_dressing_changes_per_day", "value_as_concept_id"))
    image_id                 = VirtualField(source=("row_image", "image_id"))
    guidelines_to_patient    = VirtualField(source=("row_guidelines_note", "note_text"))
    extra_notes              = VirtualField(source=("row_extra_notes", "note_text"))

    main_row = "row_procedure"
    
    row_procedure = TableBindings.ProcedureOccurrence(
        procedure_occurrence_id = FieldBind("tracking_id", key=True),
        person_id = FieldBind("patient_id"),
        provider_id = FieldBind("specialist_id"),
        procedure_concept_id = FieldBind(CID_WOUND_PHOTOGRAPHY, const=True),
        procedure_date = FieldBind("track_date"),
        procedure_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    row_fact_relation = TableBindings.FactRelationship(
        domain_concept_id_1_id = FieldBind(CID_PK_CONDITION_OCCURRENCE, const=True),
        fact_id_1 = FieldBind("wound_id"),
        relationship_concept_id = FieldBind(CID_CONDITION_RELEVANT_TO, const=True, key=True),
        domain_concept_id_2_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        fact_id_2 = FieldBind("tracking_id", key=True),
    )
    
    # Measurements
    row_length         = _tr_measurement_value_number("length", CID_WOUND_LENGTH, CID_CENTIMETER)
    row_width          = _tr_measurement_value_number("width", CID_WOUND_WIDTH, CID_CENTIMETER)
    row_exudate_amount = _tr_measurement_value_cid("exudate_amount", CID_EXUDATE_AMOUNT)
    row_exudate_type   = _tr_measurement_value_cid("exudate_type", CID_EXUDATE_APPEARANCE)    
    row_tissue_type    = _tr_measurement_value_cid("tissue_type", CID_WOUND_APPEARANCE)
    row_wound_edges    = _tr_measurement_value_cid("wound_edges", CID_WOUND_EDGE_DESCRIPTION)
    row_skin_around    = _tr_measurement_value_cid("skin_around", CID_WOUND_SKIN_AROUND)
    row_had_a_fever    = _tr_measurement_value_cid("had_a_fever", CID_FEVER)
    row_pain_level     = _tr_measurement_value_cid("pain_level", CID_PAIN_SEVERITY)
    row_dressing_changes_per_day= _tr_measurement_value_cid("dressing_changes_per_day", CID_WOUND_CARE_DRESSING_CHANGE)
    
    row_image = TableBindings.TrackingRecordImage(
        image_id           = FieldBind("image_id"),
        tracking_record_id = FieldBind("tracking_id", key=True),
    )
    # TODO verificar se deve manter nota para a imagem
    # Notes
    # row_note_image = TableBindings.Note(
    #     person_id = FieldBind("patient_id"),
    #     note_date = FieldBind("updated_at"),
    #     note_class_concept_id = FieldBind(CID_WOUND_IMAGE, const=True),
    #     encoding_concept_id = FieldBind(CID_UTF8, const=True),
    #     language_concept_id = FieldBind(CID_PORTUGUESE, const=True),
    #     note_text = FieldBind("image_id"),
    #     note_event_id = FieldBind("tracking_id", key=True),
    #     note_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
    #     note_type_concept_id = FieldBind(CID_NULL, const=True),
    # )
    
    row_guidelines_note = TableBindings.Note(
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

    row_extra_notes = TableBindings.Note(
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

class VirtualComorbidity(VirtualModel):
    comorbidity_id = VirtualField(source=("row_observation", "observation_id"), key=True)
    patient_id     = VirtualField(source=("row_observation", "person_id"))
    specialist_id  = VirtualField(source=("row_observation", "provider_id"))
    comorbidity_type = VirtualField(source=("row_observation", "value_as_concept_id"))
    # A data é gerada automaticamente quando a comorbidade é criada

    main_row = "row_observation"
    
    row_observation = TableBindings.Observation(
        observation_id = FieldBind("comorbidity_id", key=True),
        person_id = FieldBind("patient_id", key=True),
        provider_id = FieldBind("specialist_id", key=True),
        observation_concept_id = FieldBind(CID_COMORBIDITY, const=True),
        value_as_concept_id = FieldBind("comorbidity_type", key=True),
        observation_date = FieldBind(datetime.datetime.now(), const=True),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )