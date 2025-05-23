# Register your models here.
from django.contrib import admin

from .models import Specialists, Patients, Wound, Comorbidities, Images
from .omop_models import (
    CareSite, CdmSource, Cohort, CohortDefinition, Concept, ConceptAncestor,
    ConceptClass, ConceptRelationship, ConceptSynonym, ConditionEra,
    ConditionOccurrence, Cost, Death, DeviceExposure, Domain, DoseEra,
    DrugEra, DrugExposure, DrugStrength, Episode, EpisodeEvent,
    FactRelationship, Location, Measurement, Metadata, Note, NoteNlp,
    Observation, ObservationPeriod, PayerPlanPeriod, Person,
    ProcedureOccurrence, Provider, Relationship, SourceToConceptMap,
    Specimen, VisitDetail, VisitOccurrence, Vocabulary
)
admin.site.register(Specialists)
admin.site.register(Patients)
admin.site.register(Comorbidities)
admin.site.register(Images)
admin.site.register(Wound)

admin.site.register(CareSite)
admin.site.register(CdmSource)
admin.site.register(Cohort)
admin.site.register(CohortDefinition)
admin.site.register(Concept)
admin.site.register(ConceptAncestor)
admin.site.register(ConceptClass)
admin.site.register(ConceptRelationship)
admin.site.register(ConceptSynonym)
admin.site.register(ConditionEra)
admin.site.register(ConditionOccurrence)
admin.site.register(Cost)
admin.site.register(Death)
admin.site.register(DeviceExposure)
admin.site.register(Domain)
admin.site.register(DoseEra)
admin.site.register(DrugEra)
admin.site.register(DrugExposure)
admin.site.register(DrugStrength)
admin.site.register(Episode)
admin.site.register(EpisodeEvent)
admin.site.register(FactRelationship)
admin.site.register(Location)
admin.site.register(Measurement)
admin.site.register(Metadata)
admin.site.register(Note)
admin.site.register(NoteNlp)
admin.site.register(Observation)
admin.site.register(ObservationPeriod)
admin.site.register(PayerPlanPeriod)
admin.site.register(Person)
admin.site.register(ProcedureOccurrence)
admin.site.register(Provider)
admin.site.register(Relationship)
admin.site.register(SourceToConceptMap)
admin.site.register(Specimen)
admin.site.register(VisitDetail)
admin.site.register(VisitOccurrence)
admin.site.register(Vocabulary)