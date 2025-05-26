from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from drf_spectacular.utils import extend_schema
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
from .omop_serializers import (
    CareSiteSerializer, CdmSourceSerializer, CohortSerializer,
    CohortDefinitionSerializer, ConceptSerializer, ConceptAncestorSerializer,
    ConceptClassSerializer, ConceptRelationshipSerializer, ConceptSynonymSerializer,
    ConditionEraSerializer, ConditionOccurrenceSerializer, CostSerializer,
    DeathSerializer, DeviceExposureSerializer, DomainSerializer, DoseEraSerializer,
    DrugEraSerializer, DrugExposureSerializer, DrugStrengthSerializer,
    EpisodeSerializer, EpisodeEventSerializer, FactRelationshipSerializer,
    LocationSerializer, MeasurementSerializer, MetadataSerializer, NoteSerializer,
    NoteNlpSerializer, ObservationSerializer, ObservationPeriodSerializer,
    PayerPlanPeriodSerializer, PersonSerializer, ProcedureOccurrenceSerializer,
    ProviderSerializer, RelationshipSerializer, SourceToConceptMapSerializer,
    SpecimenSerializer, VisitDetailSerializer, VisitOccurrenceSerializer,
    VocabularySerializer
)


# Viewsets para cada modelo
@extend_schema(tags=["care-sites"])
class CareSiteViewSet(viewsets.ModelViewSet):
    queryset = CareSite.objects.all()
    serializer_class = CareSiteSerializer

@extend_schema(tags=["cdm-sources"])
class CdmSourceViewSet(viewsets.ModelViewSet):
    queryset = CdmSource.objects.all()
    serializer_class = CdmSourceSerializer

@extend_schema(tags=["cohorts"])
class CohortViewSet(viewsets.ModelViewSet):
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer

@extend_schema(tags=["cohort-definitions"])
class CohortDefinitionViewSet(viewsets.ModelViewSet):
    queryset = CohortDefinition.objects.all()
    serializer_class = CohortDefinitionSerializer

@extend_schema(tags=["concepts"])
class ConceptViewSet(viewsets.ModelViewSet):
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer

@extend_schema(tags=["concept-ancestors"])
class ConceptAncestorViewSet(viewsets.ModelViewSet):
    queryset = ConceptAncestor.objects.all()
    serializer_class = ConceptAncestorSerializer

@extend_schema(tags=["concept-classes"])
class ConceptClassViewSet(viewsets.ModelViewSet):
    queryset = ConceptClass.objects.all()
    serializer_class = ConceptClassSerializer

@extend_schema(tags=["concept-relationships"])
class ConceptRelationshipViewSet(viewsets.ModelViewSet):
    queryset = ConceptRelationship.objects.all()
    serializer_class = ConceptRelationshipSerializer

@extend_schema(tags=["concept-synonyms"])
class ConceptSynonymViewSet(viewsets.ModelViewSet):
    queryset = ConceptSynonym.objects.all()
    serializer_class = ConceptSynonymSerializer

@extend_schema(tags=["condition-eras"])
class ConditionEraViewSet(viewsets.ModelViewSet):
    queryset = ConditionEra.objects.all()
    serializer_class = ConditionEraSerializer

@extend_schema(tags=["condition-occurrences"])
class ConditionOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = ConditionOccurrence.objects.all()
    serializer_class = ConditionOccurrenceSerializer

@extend_schema(tags=["costs"])
class CostViewSet(viewsets.ModelViewSet):
    queryset = Cost.objects.all()
    serializer_class = CostSerializer

@extend_schema(tags=["deaths"])
class DeathViewSet(viewsets.ModelViewSet):
    queryset = Death.objects.all()
    serializer_class = DeathSerializer

@extend_schema(tags=["device-exposures"])
class DeviceExposureViewSet(viewsets.ModelViewSet):
    queryset = DeviceExposure.objects.all()
    serializer_class = DeviceExposureSerializer

@extend_schema(tags=["domains"])
class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

@extend_schema(tags=["dose-eras"])
class DoseEraViewSet(viewsets.ModelViewSet):
    queryset = DoseEra.objects.all()
    serializer_class = DoseEraSerializer

@extend_schema(tags=["drug-eras"])
class DrugEraViewSet(viewsets.ModelViewSet):
    queryset = DrugEra.objects.all()
    serializer_class = DrugEraSerializer

@extend_schema(tags=["drug-exposures"])
class DrugExposureViewSet(viewsets.ModelViewSet):
    queryset = DrugExposure.objects.all()
    serializer_class = DrugExposureSerializer

@extend_schema(tags=["drug-strengths"])
class DrugStrengthViewSet(viewsets.ModelViewSet):
    queryset = DrugStrength.objects.all()
    serializer_class = DrugStrengthSerializer

@extend_schema(tags=["episodes"])
class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer

@extend_schema(tags=["episode-events"])
class EpisodeEventViewSet(viewsets.ModelViewSet):
    queryset = EpisodeEvent.objects.all()
    serializer_class = EpisodeEventSerializer

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

@extend_schema(tags=["metadata"])
class MetadataViewSet(viewsets.ModelViewSet):
    queryset = Metadata.objects.all()
    serializer_class = MetadataSerializer

@extend_schema(tags=["notes"])
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

@extend_schema(tags=["note-nlps"])
class NoteNlpViewSet(viewsets.ModelViewSet):
    queryset = NoteNlp.objects.all()
    serializer_class = NoteNlpSerializer

@extend_schema(tags=["observations"])
class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

@extend_schema(tags=["observation-periods"])
class ObservationPeriodViewSet(viewsets.ModelViewSet):
    queryset = ObservationPeriod.objects.all()
    serializer_class = ObservationPeriodSerializer

@extend_schema(tags=["payer-plan-periods"])
class PayerPlanPeriodViewSet(viewsets.ModelViewSet):
    queryset = PayerPlanPeriod.objects.all()
    serializer_class = PayerPlanPeriodSerializer

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

@extend_schema(tags=["source-to-concept-maps"])
class SourceToConceptMapViewSet(viewsets.ModelViewSet):
    queryset = SourceToConceptMap.objects.all()
    serializer_class = SourceToConceptMapSerializer

@extend_schema(tags=["specimens"])
class SpecimenViewSet(viewsets.ModelViewSet):
    queryset = Specimen.objects.all()
    serializer_class = SpecimenSerializer

@extend_schema(tags=["visit-details"])
class VisitDetailViewSet(viewsets.ModelViewSet):
    queryset = VisitDetail.objects.all()
    serializer_class = VisitDetailSerializer

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
router.register(r'cdm-sources', CdmSourceViewSet)
router.register(r'cohorts', CohortViewSet)
router.register(r'cohort-definitions', CohortDefinitionViewSet)
router.register(r'concepts', ConceptViewSet)
router.register(r'concept-ancestors', ConceptAncestorViewSet)
router.register(r'concept-classes', ConceptClassViewSet)
router.register(r'concept-relationships', ConceptRelationshipViewSet)
router.register(r'concept-synonyms', ConceptSynonymViewSet)
router.register(r'condition-eras', ConditionEraViewSet)
router.register(r'condition-occurrences', ConditionOccurrenceViewSet)
router.register(r'costs', CostViewSet)
router.register(r'deaths', DeathViewSet)
router.register(r'device-exposures', DeviceExposureViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'dose-eras', DoseEraViewSet)
router.register(r'drug-eras', DrugEraViewSet)
router.register(r'drug-exposures', DrugExposureViewSet)
router.register(r'drug-strengths', DrugStrengthViewSet)
router.register(r'episodes', EpisodeViewSet)
router.register(r'episode-events', EpisodeEventViewSet)
router.register(r'fact-relationships', FactRelationshipViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'measurements', MeasurementViewSet)
router.register(r'metadata', MetadataViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'note-nlps', NoteNlpViewSet)
router.register(r'observations', ObservationViewSet)
router.register(r'observation-periods', ObservationPeriodViewSet)
router.register(r'payer-plan-periods', PayerPlanPeriodViewSet)
router.register(r'persons', PersonViewSet)
router.register(r'procedure-occurrences', ProcedureOccurrenceViewSet)
router.register(r'providers', ProviderViewSet)
router.register(r'relationships', RelationshipViewSet)
router.register(r'source-to-concept-maps', SourceToConceptMapViewSet)
router.register(r'specimens', SpecimenViewSet)
router.register(r'visit-details', VisitDetailViewSet)
router.register(r'visit-occurrences', VisitOccurrenceViewSet)
router.register(r'vocabularies', VocabularyViewSet)

