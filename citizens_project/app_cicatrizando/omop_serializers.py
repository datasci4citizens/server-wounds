from rest_framework import serializers
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

# Serializers para cada modelo
class CareSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareSite
        fields = '__all__'

class CdmSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CdmSource
        fields = '__all__'

class CohortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cohort
        fields = '__all__'

class CohortDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CohortDefinition
        fields = '__all__'

class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = '__all__'

class ConceptAncestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptAncestor
        fields = '__all__'

class ConceptClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptClass
        fields = '__all__'

class ConceptRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptRelationship
        fields = '__all__'

class ConceptSynonymSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptSynonym
        fields = '__all__'

class ConditionEraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionEra
        fields = '__all__'

class ConditionOccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionOccurrence
        fields = '__all__'

class CostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cost
        fields = '__all__'

class DeathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Death
        fields = '__all__'

class DeviceExposureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceExposure
        fields = '__all__'

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'

class DoseEraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoseEra
        fields = '__all__'

class DrugEraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugEra
        fields = '__all__'

class DrugExposureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugExposure
        fields = '__all__'

class DrugStrengthSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugStrength
        fields = '__all__'

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = '__all__'

class EpisodeEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeEvent
        fields = '__all__'

class FactRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactRelationship
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = '__all__'

class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        fields = '__all__'

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

class NoteNlpSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteNlp
        fields = '__all__'

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = '__all__'

class ObservationPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationPeriod
        fields = '__all__'

class PayerPlanPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayerPlanPeriod
        fields = '__all__'

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class ProcedureOccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureOccurrence
        fields = '__all__'

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = '__all__'

class SourceToConceptMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceToConceptMap
        fields = '__all__'

class SpecimenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specimen
        fields = '__all__'

class VisitDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitDetail
        fields = '__all__'

class VisitOccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitOccurrence
        fields = '__all__'

class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = '__all__'