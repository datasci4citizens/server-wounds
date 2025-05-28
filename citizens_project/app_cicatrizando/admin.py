# Register your models here.
from django.contrib import admin

from .models import Specialists, Patients, Wound, Comorbidities, Images
from .omop_models import (
    CareSite, Concept,
    ConceptClass, ConceptSynonym, ConditionOccurrence, Domain,
    FactRelationship, Location, Measurement, Note, 
    Observation, ObservationPeriod,  Person,
    ProcedureOccurrence, Provider, Relationship, VisitOccurrence, Vocabulary
)
admin.site.register(Specialists)
admin.site.register(Patients)
admin.site.register(Comorbidities)
admin.site.register(Images)
admin.site.register(Wound)

admin.site.register(CareSite)
admin.site.register(Location)
admin.site.register(ConditionOccurrence)
admin.site.register(Domain)
admin.site.register(FactRelationship)
admin.site.register(Measurement)
admin.site.register(Note)
admin.site.register(Observation)
admin.site.register(Person)
admin.site.register(ProcedureOccurrence)
admin.site.register(Provider)
admin.site.register(VisitOccurrence)

admin.site.register(ObservationPeriod)

admin.site.register(Concept)
admin.site.register(ConceptClass)
admin.site.register(ConceptSynonym)
admin.site.register(Relationship)
admin.site.register(Vocabulary)