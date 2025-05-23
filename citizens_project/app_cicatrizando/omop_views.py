from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

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
class CareSiteViewSet(viewsets.ModelViewSet):
    queryset = CareSite.objects.all()
    serializer_class = CareSiteSerializer

class CdmSourceViewSet(viewsets.ModelViewSet):
    queryset = CdmSource.objects.all()
    serializer_class = CdmSourceSerializer

class CohortViewSet(viewsets.ModelViewSet):
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer

class CohortDefinitionViewSet(viewsets.ModelViewSet):
    queryset = CohortDefinition.objects.all()
    serializer_class = CohortDefinitionSerializer

class ConceptViewSet(viewsets.ModelViewSet):
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer

class ConceptAncestorViewSet(viewsets.ModelViewSet):
    queryset = ConceptAncestor.objects.all()
    serializer_class = ConceptAncestorSerializer

class ConceptClassViewSet(viewsets.ModelViewSet):
    queryset = ConceptClass.objects.all()
    serializer_class = ConceptClassSerializer

class ConceptRelationshipViewSet(viewsets.ModelViewSet):
    queryset = ConceptRelationship.objects.all()
    serializer_class = ConceptRelationshipSerializer

class ConceptSynonymViewSet(viewsets.ModelViewSet):
    queryset = ConceptSynonym.objects.all()
    serializer_class = ConceptSynonymSerializer

class ConditionEraViewSet(viewsets.ModelViewSet):
    queryset = ConditionEra.objects.all()
    serializer_class = ConditionEraSerializer

class ConditionOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = ConditionOccurrence.objects.all()
    serializer_class = ConditionOccurrenceSerializer

class CostViewSet(viewsets.ModelViewSet):
    queryset = Cost.objects.all()
    serializer_class = CostSerializer

class DeathViewSet(viewsets.ModelViewSet):
    queryset = Death.objects.all()
    serializer_class = DeathSerializer

class DeviceExposureViewSet(viewsets.ModelViewSet):
    queryset = DeviceExposure.objects.all()
    serializer_class = DeviceExposureSerializer

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

class DoseEraViewSet(viewsets.ModelViewSet):
    queryset = DoseEra.objects.all()
    serializer_class = DoseEraSerializer

class DrugEraViewSet(viewsets.ModelViewSet):
    queryset = DrugEra.objects.all()
    serializer_class = DrugEraSerializer

class DrugExposureViewSet(viewsets.ModelViewSet):
    queryset = DrugExposure.objects.all()
    serializer_class = DrugExposureSerializer

class DrugStrengthViewSet(viewsets.ModelViewSet):
    queryset = DrugStrength.objects.all()
    serializer_class = DrugStrengthSerializer

class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer

class EpisodeEventViewSet(viewsets.ModelViewSet):
    queryset = EpisodeEvent.objects.all()
    serializer_class = EpisodeEventSerializer

class FactRelationshipViewSet(viewsets.ModelViewSet):
    queryset = FactRelationship.objects.all()
    serializer_class = FactRelationshipSerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

class MetadataViewSet(viewsets.ModelViewSet):
    queryset = Metadata.objects.all()
    serializer_class = MetadataSerializer

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

class NoteNlpViewSet(viewsets.ModelViewSet):
    queryset = NoteNlp.objects.all()
    serializer_class = NoteNlpSerializer

class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

class ObservationPeriodViewSet(viewsets.ModelViewSet):
    queryset = ObservationPeriod.objects.all()
    serializer_class = ObservationPeriodSerializer

class PayerPlanPeriodViewSet(viewsets.ModelViewSet):
    queryset = PayerPlanPeriod.objects.all()
    serializer_class = PayerPlanPeriodSerializer

class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

class ProcedureOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = ProcedureOccurrence.objects.all()
    serializer_class = ProcedureOccurrenceSerializer

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

class RelationshipViewSet(viewsets.ModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer

class SourceToConceptMapViewSet(viewsets.ModelViewSet):
    queryset = SourceToConceptMap.objects.all()
    serializer_class = SourceToConceptMapSerializer

class SpecimenViewSet(viewsets.ModelViewSet):
    queryset = Specimen.objects.all()
    serializer_class = SpecimenSerializer

class VisitDetailViewSet(viewsets.ModelViewSet):
    queryset = VisitDetail.objects.all()
    serializer_class = VisitDetailSerializer

class VisitOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = VisitOccurrence.objects.all()
    serializer_class = VisitOccurrenceSerializer

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
