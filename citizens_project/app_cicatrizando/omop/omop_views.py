from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from drf_spectacular.utils import extend_schema
from .omop_models import (
    CareSite, Concept,
    ConceptClass,  ConceptSynonym,
    ConditionOccurrence,  Domain,
    FactRelationship, Location, Measurement, Note,
    Observation, ObservationPeriod, Person,
    ProcedureOccurrence, Provider, Relationship,
    VisitOccurrence, Vocabulary
)
from .omop_serializers import (
    CareSiteSerializer,  ConceptSerializer,
    ConceptClassSerializer, ConceptSynonymSerializer,
    ConditionOccurrenceSerializer, DomainSerializer, FactRelationshipSerializer,
    LocationSerializer, MeasurementSerializer, NoteSerializer,
    ObservationSerializer, ObservationPeriodSerializer,
    PersonSerializer, ProcedureOccurrenceSerializer,
    ProviderSerializer, RelationshipSerializer,
    VisitOccurrenceSerializer, VocabularySerializer
)


# Viewsets para cada modelo
@extend_schema(tags=["care-sites"])
class CareSiteViewSet(viewsets.ModelViewSet):
    queryset = CareSite.objects.all()
    serializer_class = CareSiteSerializer

@extend_schema(tags=["concepts"])
class ConceptViewSet(viewsets.ModelViewSet):
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer

@extend_schema(tags=["concept-classes"])
class ConceptClassViewSet(viewsets.ModelViewSet):
    queryset = ConceptClass.objects.all()
    serializer_class = ConceptClassSerializer

@extend_schema(tags=["concept-synonyms"])
class ConceptSynonymViewSet(viewsets.ModelViewSet):
    queryset = ConceptSynonym.objects.all()
    serializer_class = ConceptSynonymSerializer

@extend_schema(tags=["condition-occurrences"])
class ConditionOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = ConditionOccurrence.objects.all()
    serializer_class = ConditionOccurrenceSerializer

@extend_schema(tags=["domains"])
class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

@extend_schema(tags=["fact-relationships"])
class FactRelationshipViewSet(viewsets.ModelViewSet):
    queryset = FactRelationship.objects.all()
    serializer_class = FactRelationshipSerializer

@extend_schema(tags=["locations"])
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

@extend_schema(tags=["measurements"])
class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

@extend_schema(tags=["notes"])
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

@extend_schema(tags=["observations"])
class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

@extend_schema(tags=["observation-periods"])
class ObservationPeriodViewSet(viewsets.ModelViewSet):
    queryset = ObservationPeriod.objects.all()
    serializer_class = ObservationPeriodSerializer

@extend_schema(tags=["persons"])
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

@extend_schema(tags=["procedure-occurrences"])
class ProcedureOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = ProcedureOccurrence.objects.all()
    serializer_class = ProcedureOccurrenceSerializer

@extend_schema(tags=["providers"])
class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

@extend_schema(tags=["relationships"])
class RelationshipViewSet(viewsets.ModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer

@extend_schema(tags=["visit-occurrences"])
class VisitOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = VisitOccurrence.objects.all()
    serializer_class = VisitOccurrenceSerializer

@extend_schema(tags=["vocabularies"])
class VocabularyViewSet(viewsets.ModelViewSet):
    queryset = Vocabulary.objects.all()
    serializer_class = VocabularySerializer



router = DefaultRouter()

# Registre todas as viewsets
router.register(r'care-sites', CareSiteViewSet)
router.register(r'concepts', ConceptViewSet)
router.register(r'concept-classes', ConceptClassViewSet)
router.register(r'concept-synonyms', ConceptSynonymViewSet)
router.register(r'condition-occurrences', ConditionOccurrenceViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'fact-relationships', FactRelationshipViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'measurements', MeasurementViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'observations', ObservationViewSet)
router.register(r'observation-periods', ObservationPeriodViewSet)
router.register(r'persons', PersonViewSet)
router.register(r'procedure-occurrences', ProcedureOccurrenceViewSet)
router.register(r'providers', ProviderViewSet)
router.register(r'relationships', RelationshipViewSet)
router.register(r'visit-occurrences', VisitOccurrenceViewSet)
router.register(r'vocabularies', VocabularyViewSet)

