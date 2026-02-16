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


# mapeamentos de conceitos para o OMOP CDM com choicemap

map_drink_frequency = ChoiceMap([
    ("0", omop_ids.CID_DRINK_NEVER),
    ("1", omop_ids.CID_DRINK_MONTHLY_OR_LESS),
    ("2", omop_ids.CID_DRINK_2_3_TIMES_WEEK),
    ("3", omop_ids.CID_DRINK_4_OR_MORE_WEEK),

])

map_exudate_amount = ChoiceMap([
    ("0", omop_ids.CID_NONE),
    ("1", omop_ids.CID_QUITE_A_BIT),
    ("2", omop_ids.CID_A_MODERATE_AMOUNT),
    ("3", omop_ids.CID_A_LOT),

])

map_exudate_type = ChoiceMap([
    ("0", omop_ids.CID_EXUDATE_SEROUS),
    ("1", omop_ids.CID_EXUDATE_SANGUINOUS),
    ("2", omop_ids.CID_EXUDATE_PURULENT),
    ("3", omop_ids.CID_EXUDATE_SEROSANGUINOUS),
    ("4", omop_ids.CID_FETID), # conceito local ( nao omop)
    ("5", omop_ids.CID_NONE),
])

map_skin_around = ChoiceMap([
    ("in", omop_ids.CID_SWELLING),
    ("l2", omop_ids.CID_WOUND_ERYTHEMA),
    ("g2", omop_ids.CID_WOUND_ERYTHEMA), 
])

map_smoke_frequency = ChoiceMap([
    ("0 ", omop_ids.CID_NEVER),
    ("1", omop_ids.CID_OCCASIONALLY),
    ("2", omop_ids.CID_10_OR_LESS),
    ("3", omop_ids.CID_10_OR_MORE),
])

map_tissue_type = ChoiceMap([
    ("tc", omop_ids.CID_SCAR),
    ("te", omop_ids.CID_EPITHELIALIZATION),
    ("tg", omop_ids.CID_GRANULATION),
    ("td", omop_ids.CID_DEVITALIZED), #conceito local (nao omop),
    ("tn", omop_ids.CID_NECROTIC_ISSUE_ESCHAR),
])

map_wound_edges = ChoiceMap([
    ("in", omop_ids.CID_WOUND_EDGE_POORLY_DEFINED),
    ("df", omop_ids.CID_WOUND_EDGE_ATTACHED),
    ("na", omop_ids.CID_WOUND_EDGE_NOT_ATTACHED),
    ("cu", omop_ids.CID_WOUND_EDGE_ROLLED),
    ("fb", omop_ids.CID_WOUND_EDGE_SCABBED),
])


#sao todos conceitos locais
map_wound_location = ChoiceMap([
    # Regiões Principais
    ("cb", omop_ids.CID_REGION_HEAD),
    ("fc", omop_ids.CID_REGION_FACE),
    ("pc", omop_ids.CID_REGION_NECK),
    ("pt", omop_ids.CID_REGION_CHEST),
    ("ab", omop_ids.CID_REGION_ABDOMEN),
    ("ds", omop_ids.CID_REGION_BACK),
    ("pr", omop_ids.CID_REGION_PERINEAL),
    ("ms", omop_ids.CID_REGION_UPPER_LIMB),
    ("mi", omop_ids.CID_REGION_LOWER_LIMB),

    # Sub-Regiões da Cabeça (cb)
    ("cb ft", omop_ids.CID_SUBREGION_HEAD_FRONTAL),
    ("cb pt", omop_ids.CID_SUBREGION_HEAD_PARIETAL),
    ("cb oc", omop_ids.CID_SUBREGION_HEAD_OCCIPITAL),
    ("cb tm", omop_ids.CID_SUBREGION_HEAD_TEMPORAL),
    ("cb it", omop_ids.CID_SUBREGION_HEAD_INFRATEMPORAL),

    # Sub-Regiões da Face (fc)
    ("fc ns", omop_ids.CID_SUBREGION_FACE_NASAL),
    ("fc ol", omop_ids.CID_SUBREGION_FACE_ORAL),
    ("fc mn", omop_ids.CID_SUBREGION_FACE_MENTONIAN),
    ("fc or", omop_ids.CID_SUBREGION_FACE_ORBITAL),
    ("fc io", omop_ids.CID_SUBREGION_FACE_INFRAORBITAL),
    ("fc jg", omop_ids.CID_SUBREGION_FACE_BUCCAL),
    ("fc zg", omop_ids.CID_SUBREGION_FACE_ZYGOMATIC),
    ("fc pm", omop_ids.CID_SUBREGION_FACE_PAROTIDOMASSETERIC),

    # Sub-Regiões do Pescoço (pc)
    ("pc an", omop_ids.CID_SUBREGION_NECK_ANTERIOR),
    ("pc em", omop_ids.CID_SUBREGION_NECK_STERNOCLEIDOMASTOID),
    ("pc lt", omop_ids.CID_SUBREGION_NECK_LATERAL),
    ("pc pn", omop_ids.CID_SUBREGION_NECK_POSTERIOR),

    # Sub-Regiões do Peito (pt)
    ("pt ic", omop_ids.CID_SUBREGION_CHEST_INFRACLAVICULAR),
    ("pt mm", omop_ids.CID_SUBREGION_CHEST_MAMMARY),
    ("pt ax", omop_ids.CID_SUBREGION_CHEST_AXILLARY),
    ("pt es", omop_ids.CID_SUBREGION_CHEST_STERNAL),

    # Sub-Regiões do Abdome (aecido desvitalizadob)
    ("ab hc", omop_ids.CID_SUBREGION_ABDOMEN_HYPOCHONDRIAC),
    ("ab ep", omop_ids.CID_SUBREGION_ABDOMEN_EPIGASTRIC),
    ("ab la", omop_ids.CID_SUBREGION_ABDOMEN_FLANK),
    ("ab um", omop_ids.CID_SUBREGION_ABDOMEN_UMBILICAL),
    ("ab ig", omop_ids.CID_SUBREGION_ABDOMEN_INGUINAL),
    ("ab pb", omop_ids.CID_SUBREGION_ABDOMEN_PUBIC_HYPOGASTRIC),

    # Sub-Regiões do Dorso (ds)
    ("ds vt", omop_ids.CID_SUBREGION_BACK_VERTEBRAL),
    ("ds sc", omop_ids.CID_SUBREGION_BACK_SACRAL),
    ("ds es", omop_ids.CID_SUBREGION_BACK_SCAPULAR),
    ("ds ie", omop_ids.CID_SUBREGION_BACK_INFRASCAPULAR),
    ("ds lb", omop_ids.CID_SUBREGION_BACK_LUMBAR),
    ("ds se", omop_ids.CID_SUBREGION_BACK_SUPRASCAPULAR),
    ("ds iv", omop_ids.CID_SUBREGION_BACK_INTERSCAPULOVERTEBRAL),

    # Sub-Regiões da Região Perineal (pr)
    ("pr an", omop_ids.CID_SUBREGION_PERINEAL_ANAL),
    ("pr ug", omop_ids.CID_SUBREGION_PERINEAL_UROGENITAL),

    # Sub-Regiões do Membro Superior (ms)
    ("ms dt", omop_ids.CID_SUBREGION_UPPER_LIMB_DELTOID),
    ("ms ab", omop_ids.CID_SUBREGION_UPPER_LIMB_ANTERIOR_ARM),
    ("ms pb", omop_ids.CID_SUBREGION_UPPER_LIMB_POSTERIOR_ARM),
    ("ms ac", omop_ids.CID_SUBREGION_UPPER_LIMB_ANTERIOR_ELBOW),
    ("ms pc", omop_ids.CID_SUBREGION_UPPER_LIMB_POSTERIOR_ELBOW),
    ("ms aa", omop_ids.CID_SUBREGION_UPPER_LIMB_ANTERIOR_FOREARM),
    ("ms pa", omop_ids.CID_SUBREGION_UPPER_LIMB_POSTERIOR_FOREARM),
    ("ms dm", omop_ids.CID_SUBREGION_UPPER_LIMB_DORSUM_HAND),
    ("ms pm", omop_ids.CID_SUBREGION_UPPER_LIMB_PALM_HAND),

    # Sub-Regiões do Membro Inferior (mi)
    ("mi gl", omop_ids.CID_SUBREGION_LOWER_LIMB_GLUTEAL),
    ("mi ac", omop_ids.CID_SUBREGION_LOWER_LIMB_ANTERIOR_THIGH),
    ("mi pc", omop_ids.CID_SUBREGION_LOWER_LIMB_POSTERIOR_THIGH),
    ("mi aj", omop_ids.CID_SUBREGION_LOWER_LIMB_ANTERIOR_KNEE),
    ("mi pj", omop_ids.CID_SUBREGION_LOWER_LIMB_POSTERIOR_KNEE),
    ("mi pp", omop_ids.CID_SUBREGION_LOWER_LIMB_POSTERIOR_LEG),
    ("mi ap", omop_ids.CID_SUBREGION_LOWER_LIMB_ANTERIOR_LEG),
    ("mi cl", omop_ids.CID_SUBREGION_LOWER_LIMB_CALCANEAL),
    ("mi dp", omop_ids.CID_SUBREGION_LOWER_LIMB_DORSUM_FOOT),
    ("mi ppf", omop_ids.CID_SUBREGION_LOWER_LIMB_PLANTAR_FOOT), 
])
map_is_active = ChoiceMap([
    (True, omop_ids.CID_CONDITION_ACTIVE),
    (False, omop_ids.CID_CONDITION_INACTIVE),
])
# conceitos locais
map_wound_size = ChoiceMap([
    ("0", omop_ids.CID_WOUND_AREA_0_SQCM),
    ("1", omop_ids.CID_WOUND_AREA_LT_0_3_SQCM),
    ("2", omop_ids.CID_WOUND_AREA_0_3_0_6_SQCM),
    ("3", omop_ids.CID_WOUND_AREA_0_7_1_SQCM),
    ("4", omop_ids.CID_WOUND_AREA_1_1_2_SQCM),
    ("5", omop_ids.CID_WOUND_AREA_2_1_3_SQCM),
    ("6", omop_ids.CID_WOUND_AREA_3_1_4_SQCM),
    ("7", omop_ids.CID_WOUND_AREA_4_1_8_SQCM),
    ("8", omop_ids.CID_WOUND_AREA_8_1_12_SQCM),
    ("9", omop_ids.CID_WOUND_AREA_12_1_24_SQCM),
    ("10", omop_ids.CID_WOUND_AREA_GT_24_SQCM),
])

map_wound_type = ChoiceMap([
    ("ud", omop_ids.CID_DIABETIC_FOOT_ULCER ),
    ("up", omop_ids.CID_PRESSURE_INJURY),
    ("uv", omop_ids.CID_VENEMOUS_ULCER), #conceito local (nao omop)
    ("ua", omop_ids.CID_ARTERIAL_ULCER),
    ("ft", omop_ids.CID_TRAUMATIC_WOUND),
    ("fc", omop_ids.CID_SURGICAL_WOUND),
    ("qm", omop_ids.CID_BURN),
    ("os", omop_ids.CID_OSTOMY),
    ("st", omop_ids.CID_TEAR_OF_SKIN),
    ("fs", omop_ids.CID_FISTULA),
    ("fn", omop_ids.CID_WOUND_NECROTIC),
    ("fl", omop_ids.CID_PHLEBITIS),

])

class TableBindings:
    # This class defines bindings for various database tables.
    # Each inner class links a Python object to a specific database table,
    # facilitating interaction with the database (e.g., CRUD operations).
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


# ---
# This list defines the explicit order in which database tables should be created.
# The order is crucial to respect foreign key dependencies and prevent creation errors.
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
map_had_a_fever = ChoiceMap([
    (True , omop_ids.CID_POSITIVE),
    (False, omop_ids.CID_NEGATIVE)
])

class VirtualPatient(VirtualModel):
    # Define os campos virtuais do paciente e seus mapeamentos para as tabelas OMOP.
    # 'patient_id' é a chave primária, vindo da tabela 'Person'.
    patient_id = VirtualField(source=("row_person","person_id"), key=True)
    # 'name' e 'bind_code' vêm de informações não-clínicas.
    name                  = VirtualField(source=("row_nonclinicalinfos", "name"))
    bind_code             = VirtualField(source=("row_nonclinicalinfos", "bind_code"))
    # 'gender' e 'birthday' são mapeados para a tabela 'Person'. 'gender' usa um choicemap.
    gender                = VirtualField(source=("row_person", "gender_concept_id"), choicemap=map_gender)
    birthday              = VirtualField(source=("row_person", "birth_datetime"))
    # 'specialist_id' e 'hospital_registration' são campos da tabela 'Person', com 'hospital_registration' sendo opcional.
    specialist_id         = VirtualField(source=("row_person", "provider_id"))
    hospital_registration = VirtualField(source=("row_person", "person_care_site_registration"), null=True)
    # 'phone_number' é um campo opcional de informações não-clínicas.
    phone_number          = VirtualField(source=("row_nonclinicalinfos", "phone_number"), null=True)
    # 'weight' e 'height' são medidas, permitindo valores nulos.
    weight                = VirtualField(source=("row_weight", "value_as_number"), null=True)
    height                = VirtualField(source=("row_height", "value_as_number"), null=True)
    # 'accept_tcl' (Termos e Condições) é um campo de informações não-clínicas.
    accept_tcl            = VirtualField(source=("row_nonclinicalinfos", "accept_tcl"))
    # 'smoke_frequency' e 'drink_frequency' são observações, usando choicemaps e permitindo nulos.
    smoke_frequency       = VirtualField(source=("row_smoke_frequency", "value_as_concept_id"), choicemap=map_smoke_frequency, null=True)
    drink_frequency       = VirtualField(source=("row_drink_frequency", "value_as_concept_id"), choicemap=map_drink_frequency, null=True)
    # 'user_id' é uma ligação opcional ao usuário do sistema.
    user_id               = VirtualField(source=("row_person", "person_user_id"), null=True)
    # 'updated_at' é mapeado para a data da medição de altura, servindo como uma data de última atualização.
    updated_at            = VirtualField(source=("row_height", "measurement_date"))
    # Define 'row_person' como a tabela principal para o VirtualPatient.
    main_row = "row_person"

    # Mapeamento detalhado dos campos virtuais para as colunas da tabela OMOP 'Person'.
    row_person = TableBindings.Person(
        person_id                     = FieldBind("patient_id", key = True),
        birth_datetime                = FieldBind("birthday"),
        year_of_birth                 = FieldBind(CID_NULL, const=True), # Campos constantes que não são mapeados dinamicamente.
        race_concept_id               = FieldBind(CID_NULL, const=True),
        ethnicity_concept_id          = FieldBind(CID_NULL, const=True),
        gender_concept_id             = FieldBind("gender"),
        provider_id                   = FieldBind("specialist_id"),
        person_care_site_registration = FieldBind("hospital_registration"),
        person_user_id                = FieldBind("user_id")
    )
    # Mapeamento para a tabela de informações não-clínicas do paciente.
    row_nonclinicalinfos = TableBindings.PatientNonClinicalInfos(
        person_id    = FieldBind("patient_id", key=True),
        name         = FieldBind("name"),
        phone_number = FieldBind("phone_number"),
        accept_tcl   = FieldBind("accept_tcl"),
        bind_code    = FieldBind("bind_code")
    )
    
    # Mapeamento para a tabela de medidas (Measurement) para altura. Inclui conceitos constantes para tipo e unidade.
    row_height = TableBindings.Measurement( 
        person_id              = FieldBind("patient_id", key = True),
        value_as_number        = FieldBind("height"),
        measurement_concept_id = FieldBind(CID_HEIGHT, const=True, key = True),
        unit_concept_id        = FieldBind(CID_CENTIMETER, const=True),
        measurement_date       = FieldBind("updated_at"),
        measurement_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    # Mapeamento para a tabela de medidas (Measurement) para peso.
    row_weight = TableBindings.Measurement(
        person_id              = FieldBind("patient_id", key = True),
        value_as_number        = FieldBind("weight"),
        measurement_concept_id = FieldBind(CID_WEIGHT, const=True, key = True),
        unit_concept_id        = FieldBind(CID_KILOGRAM, const=True),
        measurement_date       = FieldBind("updated_at"),
        measurement_type_concept_id = FieldBind(CID_NULL, const=True),
    )

    # Mapeamento para a tabela de observações (Observation) para frequência de fumo.
    row_smoke_frequency = TableBindings.Observation(
        person_id                   = FieldBind("patient_id", key = True),
        observation_concept_id      = FieldBind(CID_SMOKE_FREQUENCY, const=True, key = True),
        value_as_concept_id         = FieldBind("smoke_frequency"),
        observation_date            = FieldBind("updated_at"),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )

    # Mapeamento para a tabela de observações (Observation) para frequência de bebida.
    row_drink_frequency = TableBindings.Observation(
        person_id                   = FieldBind("patient_id", key = True),
        observation_concept_id      = FieldBind(CID_DRINK_FREQUENCY, const=True, key = True),
        value_as_concept_id         = FieldBind("drink_frequency"),
        observation_date            = FieldBind("updated_at"),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    # Método de classe para obter as comorbidades de um paciente específico.
    @classmethod
    def get_comorbidities(cls, patient_id : int):
        # Filtra as observações relacionadas ao paciente e ao conceito de comorbidade.
        queryset = Observation.objects.all().filter(person_id=patient_id, observation_concept_id=omop_ids.CID_COMORBIDITY)
        comorbidities = []
        # Converte os IDs de conceito OMOP de comorbidades para seus valores virtuais legíveis.
        for c in queryset:
            comorbidities.append(map_comorbidities.db_to_virtual(c.value_as_concept_id))
            
        return comorbidities

class VirtualSpecialist(VirtualModel):
    # Define os campos virtuais para um especialista e seus mapeamentos.
    # 'specialist_id' é a chave primária, mapeada para 'provider_id'.
    specialist_id   = VirtualField(source=("row_provider", "provider_id"), key=True)
    # 'specialist_name' e 'user_id' são campos do provedor.
    specialist_name = VirtualField(source=("row_provider", "provider_name"))
    user_id         = VirtualField(source=("row_provider", "provider_user_id")), 
    # 'birthday' e 'speciality' são campos opcionais do provedor.
    birthday        = VirtualField(source=("row_provider", "provider_birthday"), null=True)
    speciality      = VirtualField(source=("row_provider", "specialty_string"), null=True)
    # 'city' e 'state' são campos opcionais da localização.
    city            = VirtualField(source=("row_location", "city"), null=True)
    state           = VirtualField(source=("row_location", "state"), null=True)
    # Define 'row_provider' como a tabela principal para o VirtualSpecialist.
    main_row = "row_provider"
    # Mapeamento detalhado para a tabela OMOP 'Provider'.
    row_provider = TableBindings.Provider(
        provider_id       = FieldBind("specialist_id", key = True),
        provider_name     = FieldBind("specialist_name"),
        provider_birthday = FieldBind("birthday"),
        provider_user_id  = FieldBind("user_id"),
        specialty_string  = FieldBind("speciality")
    )

    # Mapeamento para a tabela OMOP 'Location', associada ao especialista.
    row_location =  TableBindings.Location(
        location_id = FieldBind("specialist_id", key=True),
        city        = FieldBind("city"),  
        state       = FieldBind("state"),  
    )

class VirtualWound(VirtualModel):
    # Define os campos virtuais para uma ferida e seus mapeamentos.
    # 'wound_id' é a chave primária, mapeada para 'condition_occurrence_id'.
    wound_id      = VirtualField(source=("row_condition", "condition_occurrence_id"), key=True)
    # 'region' e 'wound_type' são mapeados para conceitos OMOP usando choicemaps.
    region        = VirtualField(source=("row_region", "value_as_concept_id"), choicemap=map_wound_location)
    wound_type    = VirtualField(source=("row_condition", "condition_concept_id"), choicemap=map_wound_type) 
    # 'start_date', 'end_date' (opcional) e 'is_active' são campos da condição.
    start_date    = VirtualField(source=("row_condition", "condition_start_date"))
    end_date      = VirtualField(source=("row_condition", "condition_end_date"), null=True)
    is_active     = VirtualField(source=("row_condition", "condition_status_concept_id"), choicemap=map_is_active)
    # 'image_id' é opcional e mapeado para 'WoundImage'.
    image_id      = VirtualField(source=("row_image", "image_id"), null=True)
    # 'patient_id' e 'specialist_id' são campos da condição.
    patient_id    = VirtualField(source=("row_condition", "person_id"))
    specialist_id = VirtualField(source=("row_condition", "provider_id"))
    # 'updated_at' é mapeado para a data da observação da região.
    updated_at    = VirtualField(source=("row_region", "observation_date"))
    # Define 'row_condition' como a tabela principal para a VirtualWound.
    main_row = "row_condition"
    # Mapeamento detalhado para a tabela OMOP 'ConditionOccurrence'.
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
    
    # Mapeamento para a tabela OMOP 'Observation' para a região da ferida.
    row_region = TableBindings.Observation(
        person_id                   = FieldBind("patient_id", key=True),
        observation_concept_id      = FieldBind(CID_WOUND_LOCATION, const=True, key=True),
        observation_date            = FieldBind("updated_at"),
        value_as_concept_id         = FieldBind("region"),
        observation_event_id        = FieldBind("wound_id", key=True),
        obs_event_field_concept_id  = FieldBind(CID_PK_CONDITION_OCCURRENCE, const=True),
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    # Mapeamento para a tabela 'WoundImage' que associa a imagem à ferida.
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


# Função auxiliar para criar um mapeamento para a tabela OMOP 'Measurement'.
def _tr_measurement(**kwargs):
    return TableBindings.Measurement(
        person_id = FieldBind("patient_id", key=True),
        measurement_date = FieldBind("track_date"),
        measurement_event_id = FieldBind("tracking_id", key=True),
        meas_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        measurement_type_concept_id = FieldBind(CID_NULL, const=True),
        **kwargs
    )
# Função auxiliar para criar um mapeamento de Measurement onde o valor é um Concept ID.
def _tr_measurement_value_cid(virtual: str, concept: int):
    return _tr_measurement(
        value_as_concept_id = FieldBind(virtual),   
        measurement_concept_id = FieldBind(concept, const = True, key=True)
    )    

# Função auxiliar para criar um mapeamento de Measurement onde o valor é um número.
def _tr_measurement_value_number(virtual: str, concept: int, cid_unit : int):
    return _tr_measurement(
        value_as_number = FieldBind(virtual),   
        measurement_concept_id = FieldBind(concept, const = True, key=True),
        unit_concept_id = FieldBind(cid_unit, const = True)
    )    
class VirtualTrackingRecords(VirtualModel):
    # Define os campos virtuais para um registro de acompanhamento e seus mapeamentos.
    # 'tracking_id' é a chave primária, mapeada para 'procedure_occurrence_id'.
    tracking_id              = VirtualField(source=("row_procedure", "procedure_occurrence_id"), key=True)
    # 'patient_id' e 'specialist_id' vêm da tabela de procedimento.
    patient_id               = VirtualField(source=("row_procedure", "person_id"))
    specialist_id            = VirtualField(source=("row_procedure", "provider_id"))
    # 'track_date' é a data do procedimento.
    track_date               = VirtualField(source=("row_procedure", "procedure_date"))
    # 'wound_id' é obtido através de uma relação de fato.
    wound_id                 = VirtualField(source=("row_fact_relation", "fact_id_1"))
    # Medidas como comprimento, largura, exsudato, tipo de tecido, etc., são mapeadas para observações/medidas.
    length                   = VirtualField(source=("row_length", "value_as_number"), null=True)
    width                    = VirtualField(source=("row_width", "value_as_number"), null=True)
    exudate_amount           = VirtualField(source=("row_exudate_amount", "value_as_concept_id"),choicemap=map_exudate_amount, null=True)
    exudate_type             = VirtualField(source=("row_exudate_type", "value_as_concept_id"),  choicemap=map_exudate_type, null=True)
    tissue_type              = VirtualField(source=("row_tissue_type", "value_as_concept_id"),   choicemap=map_tissue_type, null=True)
    wound_edges              = VirtualField(source=("row_wound_edges", "value_as_concept_id"),   choicemap=map_wound_edges, null=True)
    skin_around              = VirtualField(source=("row_skin_around", "value_as_concept_id"),   choicemap=map_skin_around, null=True)
    had_a_fever              = VirtualField(source=("row_had_a_fever", "value_as_concept_id"),   choicemap=map_had_a_fever)
    pain_level               = VirtualField(source=("row_pain_level", "value_as_number"), null=True)
    dressing_changes_per_day = VirtualField(source=("row_dressing_changes_per_day", "value_as_number"), null=True)
    # 'image_id' é opcional.
    image_id                 = VirtualField(source=("row_image", "image_id"), null=True)
    # Orientações e notas extras são mapeadas para a tabela 'Note'.
    guidelines_to_patient    = VirtualField(source=("row_guidelines_note", "note_text"))
    extra_notes              = VirtualField(source=("row_extra_notes", "note_text"))

    # Define 'row_procedure' como a tabela principal para o VirtualTrackingRecords.
    main_row = "row_procedure"
    
    # Mapeamento para a tabela OMOP 'ProcedureOccurrence' que representa o registro de acompanhamento.
    row_procedure = TableBindings.ProcedureOccurrence(
        procedure_occurrence_id = FieldBind("tracking_id", key=True),
        person_id = FieldBind("patient_id"),
        provider_id = FieldBind("specialist_id"),
        procedure_concept_id = FieldBind(CID_WOUND_PHOTOGRAPHY, const=True), # Indica que é uma fotografia da ferida.
        procedure_date = FieldBind("track_date"),
        procedure_type_concept_id = FieldBind(CID_NULL, const=True),
    )
    
    # Mapeamento para a tabela OMOP 'FactRelationship' que liga o registro de acompanhamento à ferida.
    row_fact_relation = TableBindings.FactRelationship(
        domain_concept_id_1_id = FieldBind(CID_PK_CONDITION_OCCURRENCE, const=True), # Domínio do fato 1 é Condição.
        fact_id_1 = FieldBind("wound_id"), # ID do fato 1 é o ID da ferida.
        relationship_concept_id = FieldBind(CID_CONDITION_RELEVANT_TO, const=True, key=True), # Tipo de relacionamento.
        domain_concept_id_2_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True), # Domínio do fato 2 é Procedimento.
        fact_id_2 = FieldBind("tracking_id", key=True), # ID do fato 2 é o ID do acompanhamento.
    )
    
    # Mapeamentos para as diversas medições, usando as funções auxiliares.
    row_length         = _tr_measurement_value_number("length", CID_WOUND_LENGTH, CID_CENTIMETER)
    row_width          = _tr_measurement_value_number("width", CID_WOUND_WIDTH, CID_CENTIMETER)
    row_exudate_amount = _tr_measurement_value_cid("exudate_amount", CID_EXUDATE_AMOUNT)
    row_exudate_type   = _tr_measurement_value_cid("exudate_type", CID_EXUDATE_APPEARANCE)    
    row_tissue_type    = _tr_measurement_value_cid("tissue_type", CID_WOUND_APPEARANCE)
    row_wound_edges    = _tr_measurement_value_cid("wound_edges", CID_WOUND_EDGE_DESCRIPTION)
    row_skin_around    = _tr_measurement_value_cid("skin_around", CID_WOUND_SKIN_AROUND)
    row_had_a_fever    = _tr_measurement_value_cid("had_a_fever", CID_FEVER)
    row_pain_level     = _tr_measurement_value_number("pain_level", CID_PAIN_SEVERITY, CID_NULL)
    row_dressing_changes_per_day= _tr_measurement_value_number("dressing_changes_per_day", CID_WOUND_CARE_DRESSING_CHANGE, CID_NULL)
    
    # Mapeamento para a tabela 'TrackingRecordImage' que associa a imagem ao registro de acompanhamento.
    row_image = TableBindings.TrackingRecordImage(
        image_id           = FieldBind("image_id"),
        tracking_record_id = FieldBind("tracking_id", key=True),
    )
    # TODO verificar se deve manter nota para a imagem
    # Notes
    # row_note_image = TableBindings.Note(
    #     person_id = FieldBind("patient_id"),
    #     note_date = FieldBind("track_date"),
    #     note_class_concept_id = FieldBind(CID_WOUND_IMAGE, const=True),
    #     encoding_concept_id = FieldBind(CID_UTF8, const=True),
    #     language_concept_id = FieldBind(CID_PORTUGUESE, const=True),
    #     note_text = FieldBind("image_id"),
    #     note_event_id = FieldBind("tracking_id", key=True),
    #     note_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
    #     note_type_concept_id = FieldBind(CID_NULL, const=True),
    # )
    
    # Mapeamento para a tabela OMOP 'Note' para diretrizes ao paciente.
    row_guidelines_note = TableBindings.Note(
        person_id = FieldBind("patient_id"),
        note_date = FieldBind("track_date"),
        note_class_concept_id = FieldBind(CID_WOUND_MANAGEMENT_NOTE, const=True, key = True), # Tipo de nota: gerenciamento de ferida.
        encoding_concept_id = FieldBind(CID_UTF8, const=True),
        language_concept_id = FieldBind(CID_PORTUGUESE, const=True),
        note_text = FieldBind("guidelines_to_patient"),
        note_event_id = FieldBind("tracking_id", key=True),
        note_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        note_type_concept_id = FieldBind(CID_NULL, const=True),
    )

    # Mapeamento para a tabela OMOP 'Note' para notas extras.
    row_extra_notes = TableBindings.Note(
        person_id = FieldBind("patient_id"),
        note_date = FieldBind("track_date"),
        note_class_concept_id = FieldBind(CID_GENERIC_NOTE, const=True, key = True), # Tipo de nota: genérica.
        encoding_concept_id = FieldBind(CID_UTF8, const=True),
        language_concept_id = FieldBind(CID_PORTUGUESE, const=True),
        note_text = FieldBind("extra_notes"),
        note_event_id = FieldBind("tracking_id", key=True),
        note_event_field_concept_id = FieldBind(CID_PK_PROCEDURE_OCCURRENCE, const=True),
        note_type_concept_id = FieldBind(CID_NULL, const=True),
    )

class VirtualComorbidity(VirtualModel):
    # Define os campos virtuais para uma comorbidade e seus mapeamentos.
    # 'comorbidity_id' é a chave primária, mapeada para 'observation_id'.
    comorbidity_id = VirtualField(source=("row_observation", "observation_id"), key=True)
    # 'patient_id' e 'specialist_id' são campos da observação.
    patient_id     = VirtualField(source=("row_observation", "person_id"))
    specialist_id  = VirtualField(source=("row_observation", "provider_id"))
    # 'comorbidity_type' é o tipo da comorbidade como um Concept ID.
    comorbidity_type = VirtualField(source=("row_observation", "value_as_concept_id"))
    # A data é gerada automaticamente quando a comorbidade é criada (definido no FieldBind).

    # Define 'row_observation' como a tabela principal para a VirtualComorbidity.
    main_row = "row_observation"
    
    # Mapeamento detalhado para a tabela OMOP 'Observation' para comorbidades.
    row_observation = TableBindings.Observation(
        observation_id = FieldBind("comorbidity_id", key=True),
        person_id = FieldBind("patient_id", key=True),
        provider_id = FieldBind("specialist_id", key=True),
        observation_concept_id = FieldBind(CID_COMORBIDITY, const=True), # Indica que esta observação é uma comorbidade.
        value_as_concept_id = FieldBind("comorbidity_type", key=True),
        observation_date = FieldBind(datetime.datetime.now(), const=True), # A data da observação é definida como o momento atual.
        observation_type_concept_id = FieldBind(CID_NULL, const=True),
    )