from rest_framework import serializers
from .omop_models import (
    CareSite, Concept,
    ConceptClass, ConceptSynonym,
    ConditionOccurrence, Domain,
    FactRelationship, Location, Measurement, Note,
    Observation, ObservationPeriod, Person,
    ProcedureOccurrence, Provider, Relationship,
    VisitOccurrence, Vocabulary
)

class CareSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareSite
        fields = '__all__'

class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = '__all__'

class ConceptClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptClass
        fields = '__all__'

class ConceptSynonymSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptSynonym
        fields = '__all__'

class ConditionOccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionOccurrence
        fields = '__all__'

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
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

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = '__all__'

class ObservationPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationPeriod
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

class VisitOccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitOccurrence
        fields = '__all__'

class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = '__all__'