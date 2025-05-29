# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class CareSite(models.Model):
    care_site_id = models.IntegerField(primary_key=True)
    care_site_name = models.CharField(max_length=255, blank=True, null=True)
    place_of_service_concept = models.ForeignKey('Concept', models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey('Location', models.DO_NOTHING, blank=True, null=True)
    class Meta:
        db_table = 'care_site'

class Concept(models.Model):
    concept_id = models.IntegerField(primary_key=True)
    concept_name = models.CharField(max_length=255)
    domain = models.ForeignKey('Domain', models.DO_NOTHING, null=True)
    vocabulary = models.ForeignKey('Vocabulary', models.DO_NOTHING, null=True)
    concept_class = models.ForeignKey('ConceptClass', models.DO_NOTHING, null=True)
    standard_concept = models.CharField(max_length=1, blank=True, null=True)
    concept_code = models.CharField(max_length=50, null=True)
    valid_start_date = models.DateField(null=True)
    valid_end_date = models.DateField(null=True)
    invalid_reason = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        db_table = 'concept'


class ConceptClass(models.Model):
    concept_class_id = models.CharField(primary_key=True, max_length=20)
    concept_class_name = models.CharField(max_length=255)
    concept_class_concept = models.ForeignKey(Concept, models.DO_NOTHING)

    class Meta:
        db_table = 'concept_class'


class ConceptSynonym(models.Model):
    concept = models.ForeignKey(Concept, models.DO_NOTHING)
    concept_synonym_name = models.CharField(max_length=1000)
    language_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='conceptsynonym_language_concept_set')

    class Meta:
        db_table = 'concept_synonym'

class ConditionOccurrence(models.Model):
    condition_occurrence_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)
    condition_concept = models.ForeignKey(Concept, models.DO_NOTHING)
    condition_start_date = models.DateField()
    condition_start_datetime = models.DateTimeField(blank=True, null=True)
    condition_end_date = models.DateField(blank=True, null=True)
    condition_end_datetime = models.DateTimeField(blank=True, null=True)
    condition_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='conditionoccurrence_condition_type_concept_set')
    condition_status_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='conditionoccurrence_condition_status_concept_set', blank=True, null=True)
    stop_reason = models.CharField(max_length=20, blank=True, null=True)
    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'condition_occurrence'



class Domain(models.Model):
    domain_id = models.CharField(primary_key=True, max_length=20)
    domain_name = models.CharField(max_length=255)
    domain_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='domain_concept_set')

    class Meta:
        db_table = 'domain'

class FactRelationship(models.Model):
    domain_concept_id_1 = models.ForeignKey(Concept, models.DO_NOTHING, db_column='domain_concept_id_1')
    fact_id_1 = models.IntegerField()
    domain_concept_id_2 = models.ForeignKey(Concept, models.DO_NOTHING, db_column='domain_concept_id_2', related_name='factrelationship_domain_concept_id_2_set')
    fact_id_2 = models.IntegerField()
    relationship_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='factrelationship_relationship_concept_set')

    class Meta:
        db_table = 'fact_relationship'

class Location(models.Model):
    location_id = models.IntegerField(primary_key=True)
    address_1 = models.CharField(max_length=50, blank=True, null=True)
    address_2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip = models.CharField(max_length=9, blank=True, null=True)
    county = models.CharField(max_length=20, blank=True, null=True)
    country_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    longitude = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        db_table = 'location'


class Measurement(models.Model):
    measurement_id = models.AutoField(primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)
    measurement_concept = models.ForeignKey(Concept, models.DO_NOTHING)
    measurement_date = models.DateField()
    measurement_datetime = models.DateTimeField(blank=True, null=True)
    measurement_time = models.CharField(max_length=10, blank=True, null=True)
    measurement_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='measurement_measurement_type_concept_set')
    operator_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='measurement_operator_concept_set', blank=True, null=True)
    value_as_number = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    value_as_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='measurement_value_as_concept_set', blank=True, null=True)
    unit_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='measurement_unit_concept_set', blank=True, null=True)
    range_low = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    range_high = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
    measurement_event_id = models.IntegerField(blank=True, null=True)
    meas_event_field_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='measurement_meas_event_field_concept_set', blank=True, null=True)

    class Meta:
        db_table = 'measurement'


class Note(models.Model):
    note_id = models.AutoField(primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)
    note_date = models.DateField()
    note_datetime = models.DateTimeField(blank=True, null=True)
    note_type_concept = models.ForeignKey(Concept, models.DO_NOTHING)
    note_class_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='note_note_class_concept_set')
    note_title = models.CharField(max_length=250, blank=True, null=True)
    note_text = models.TextField()
    encoding_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='note_encoding_concept_set')
    language_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='note_language_concept_set')
    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
    note_event_id = models.IntegerField(blank=True, null=True)
    note_event_field_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='note_note_event_field_concept_set', blank=True, null=True)

    class Meta:
        db_table = 'note'

class Observation(models.Model):
    observation_id = models.AutoField(primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)
    observation_concept = models.ForeignKey(Concept, models.DO_NOTHING)
    observation_date = models.DateField()
    observation_datetime = models.DateTimeField(blank=True, null=True)
    observation_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='observation_observation_type_concept_set')
    value_as_number = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    value_as_string = models.CharField(max_length=60, blank=True, null=True)
    value_as_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='observation_value_as_concept_set', blank=True, null=True)
    qualifier_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='observation_qualifier_concept_set', blank=True, null=True)
    unit_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='observation_unit_concept_set', blank=True, null=True)
    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
    observation_event_id = models.IntegerField(blank=True, null=True)
    obs_event_field_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='observation_obs_event_field_concept_set', blank=True, null=True)

    class Meta:
        db_table = 'observation'


class ObservationPeriod(models.Model):
    observation_period_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)
    observation_period_start_date = models.DateField()
    observation_period_end_date = models.DateField()
    period_type_concept = models.ForeignKey(Concept, models.DO_NOTHING)

    class Meta:
        db_table = 'observation_period'

class Person(models.Model):
    person_id = models.IntegerField(primary_key=True)
    gender_concept = models.ForeignKey(Concept, models.DO_NOTHING)
    year_of_birth = models.IntegerField()
    birth_datetime = models.DateTimeField(blank=True, null=True)
    race_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='person_race_concept_set')
    ethnicity_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='person_ethnicity_concept_set')
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    care_site = models.ForeignKey(CareSite, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'person'


class ProcedureOccurrence(models.Model):
    procedure_occurrence_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING)
    procedure_concept = models.ForeignKey(Concept, models.DO_NOTHING)
    procedure_date = models.DateField()
    procedure_datetime = models.DateTimeField(blank=True, null=True)
    procedure_end_date = models.DateField(blank=True, null=True)
    procedure_end_datetime = models.DateTimeField(blank=True, null=True)
    procedure_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='procedureoccurrence_procedure_type_concept_set')
    modifier_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='procedureoccurrence_modifier_concept_set', blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'procedure_occurrence'


class Provider(models.Model):
    provider_id = models.IntegerField(primary_key=True)
    provider_name = models.CharField(max_length=255, blank=True, null=True)
    npi = models.CharField(max_length=20, blank=True, null=True)
    dea = models.CharField(max_length=20, blank=True, null=True)
    specialty_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
    care_site = models.ForeignKey(CareSite, models.DO_NOTHING, blank=True, null=True)
    year_of_birth = models.IntegerField(blank=True, null=True)
    gender_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='provider_gender_concept_set', blank=True, null=True)

    class Meta:
        db_table = 'provider'


class Relationship(models.Model):
    relationship_id = models.CharField(primary_key=True, max_length=20)
    relationship_name = models.CharField(max_length=255)
    is_hierarchical = models.CharField(max_length=1)
    defines_ancestry = models.CharField(max_length=1)
    reverse_relationship_id = models.CharField(max_length=20)
    relationship_concept = models.ForeignKey(Concept, models.DO_NOTHING)

    class Meta:
        db_table = 'relationship'


class VisitOccurrence(models.Model):
    visit_occurrence_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING)
    visit_concept = models.ForeignKey(Concept, models.DO_NOTHING)
    visit_start_date = models.DateField()
    visit_start_datetime = models.DateTimeField(blank=True, null=True)
    visit_end_date = models.DateField()
    visit_end_datetime = models.DateTimeField(blank=True, null=True)
    visit_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='visitoccurrence_visit_type_concept_set')
    provider = models.ForeignKey(Provider, models.DO_NOTHING, blank=True, null=True)
    care_site = models.ForeignKey(CareSite, models.DO_NOTHING, blank=True, null=True)
    admitted_from_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='visitoccurrence_admitted_from_concept_set', blank=True, null=True)
    discharged_to_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='visitoccurrence_discharged_to_concept_set', blank=True, null=True)
    preceding_visit_occurrence = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'visit_occurrence'


class Vocabulary(models.Model):
    vocabulary_id = models.CharField(primary_key=True, max_length=20)
    vocabulary_name = models.CharField(max_length=255)
    vocabulary_reference = models.CharField(max_length=255, blank=True, null=True)
    vocabulary_version = models.CharField(max_length=255, blank=True, null=True)
    vocabulary_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name='vocabulary_concept_set')

    class Meta:
        db_table = 'vocabulary'

