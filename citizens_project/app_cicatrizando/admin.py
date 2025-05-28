# Register your models here.
from django.contrib import admin
from .omop.omop_models import (
    CareSite, Concept,
    ConceptClass, ConceptSynonym, ConditionOccurrence, Domain,
    FactRelationship, Location, Measurement, Note, 
    Observation, ObservationPeriod,  Person,
    ProcedureOccurrence, Provider, Relationship, VisitOccurrence, Vocabulary
)


# Register OMOP models
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