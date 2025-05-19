from django.db import models
from django.utils import timezone
import uuid
import os

""" PROVIDER - Replaces Specialists """
class Provider(models.Model):
    provider_id = models.AutoField(primary_key=True)  # OMOP standard primary key
    provider_name = models.CharField(max_length=255)  # Was specialist_name
    email = models.EmailField()
    birth_datetime = models.DateTimeField(null=True, blank=True)  # Was birthday
    specialty_concept_id = models.CharField(max_length=255, null=True, blank=True)  # Was speciality
    city = models.CharField(max_length=255, null=True, blank=True)  # Was city_character
    state = models.CharField(max_length=2, null=True, blank=True)  # Was state_character
    specialty_source_value = models.CharField(max_length=255, null=True, blank=True)  # Was specialist_character
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.provider_name

""" PERSON - Replaces Patients """
class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    gender_concept_id = models.CharField(max_length=10)
    birth_datetime = models.DateTimeField()
    person_source_value = models.CharField(max_length=255)
    email = models.EmailField()
    height_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    smoking_status = models.CharField(max_length=20, null=True, blank=True)
    alcohol_use = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    consent_flag = models.BooleanField(default=False)
    provider_id = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True, related_name='persons')
    hospital_registration = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.person_source_value


""" CONDITION_CONCEPT - Replaces Comorbidities """
class ConditionConcept(models.Model):
    condition_concept_id = models.AutoField(primary_key=True)  # OMOP standard primary key
    condition_source_value = models.CharField(max_length=255)  # Was name
    
    def __str__(self):
        return self.condition_source_value


""" CONDITION_OCCURRENCE - Links Person and ConditionConcept """
class ConditionOccurrence(models.Model):
    condition_occurrence_id = models.AutoField(primary_key=True)  # OMOP standard primary key
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='conditions')
    condition_concept_id = models.ForeignKey(ConditionConcept, on_delete=models.CASCADE)
    condition_start_datetime = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.person_id.person_source_value} - {self.condition_concept_id.condition_source_value}"


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images', filename)


""" NOTE_ATTACHMENT - Replaces Images """
class NoteAttachment(models.Model):
    note_attachment_id = models.AutoField(primary_key=True)  # OMOP standard primary key
    attachment = models.ImageField(upload_to=get_file_path)  # Was image
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Attachment {self.note_attachment_id}"


""" OBSERVATION - Replaces Wound """
class Observation(models.Model):
    observation_id = models.AutoField(primary_key=True)  # OMOP standard primary key
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='observations')  # Was patient_id
    provider_id = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True, related_name='observations')  # Was specialist_id
    observation_concept_id = models.CharField(max_length=50)  # Was type
    observation_date = models.DateTimeField()  # Was start_date
    observation_end_date = models.DateTimeField(null=True, blank=True)  # Was end_date
    body_site_concept_id = models.CharField(max_length=100)  # Was region
    body_site_detail = models.CharField(max_length=100, null=True, blank=True)  # Was subregion
    value_as_concept_id = models.CharField(max_length=50, default="Active")  # Was is_active (Active/Inactive)
    note_attachment_id = models.ForeignKey(NoteAttachment, on_delete=models.SET_NULL, null=True, blank=True)  # Was image_id
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.observation_concept_id} observation - {self.person_id.person_source_value}"


""" MEASUREMENT - Replaces TrackingRecords """
class Measurement(models.Model):
    measurement_id = models.AutoField(primary_key=True)  # OMOP standard primary key
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='measurements')
    measurement_date = models.DateTimeField()  # Was track_date
    measurement_concept_id = models.CharField(max_length=50, default="Wound")  # Type of measurement
    value_as_number_length = models.FloatField()  # Was length
    value_as_number_width = models.FloatField()  # Was width
    provider_id = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, blank=True, related_name='measurements')  # Was specialist_id
    observation_id = models.ForeignKey(Observation, on_delete=models.CASCADE, related_name='measurements')  # Was wound_id
    exudate_amount = models.CharField(max_length=50)
    exudate_type = models.CharField(max_length=50)
    tissue_type = models.CharField(max_length=50)
    wound_edges = models.CharField(max_length=100, null=True, blank=True)
    skin_around = models.CharField(max_length=100, null=True, blank=True)
    had_a_fever = models.BooleanField(null=True, blank=True)
    pain_level = models.CharField(max_length=20, null=True, blank=True)
    dressing_changes = models.CharField(max_length=20, null=True, blank=True)  # Was dressing_changer_per_day
    care_instructions = models.CharField(max_length=255, null=True, blank=True)  # Was guidelines_to_patient
    note_text = models.CharField(max_length=255, null=True, blank=True)  # Was extra_notes
    note_attachment_id = models.ForeignKey(NoteAttachment, on_delete=models.SET_NULL, null=True, blank=True)  # Was image_id
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Measurement {self.measurement_id} - {self.measurement_date}"