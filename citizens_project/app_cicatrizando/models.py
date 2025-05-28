from django.db import models
from django.utils import timezone
import uuid
import os

# modelo de banco de dados

""" SPECIALIST MODEL """
class Specialists(models.Model):
    specialist_id = models.AutoField(primary_key=True)
    specialist_name = models.CharField(max_length=255)
    email = models.EmailField()
    birthday = models.DateTimeField(null=True, blank=True)
    speciality = models.CharField(max_length=255, null=True, blank=True)
    city_character = models.CharField(max_length=255, null=True, blank=True)
    state_character = models.CharField(max_length=2, null=True, blank=True)
    specialist_character = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.specialist_name
    
 
""" COMORBIDITIES MODEL """
class Comorbidities(models.Model):
    comorbidity_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

""" PATIENT MODEL """
class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    gender = models.CharField(max_length=10)
    birthday = models.DateTimeField()
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    smoke_frequency = models.CharField(max_length=20, null=True, blank=True)
    drink_frequency = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    accept_tcl = models.BooleanField(default=False)
    specialist_id = models.ForeignKey(Specialists, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')
    hospital_registration = models.CharField(max_length=50, null=True, blank=True)
    comorbidities = models.ManyToManyField(Comorbidities, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images', filename)


""" IMAGES MODEL """
class Images(models.Model):
    image_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to=get_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Image {self.image_id}"

""" WOUND MODEL """
class Wound(models.Model):
    wound_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name='wounds')
    specialist_id = models.ForeignKey(Specialists, on_delete=models.SET_NULL, null=True, blank=True, related_name='wounds')
    region = models.CharField(max_length=100)
    subregion = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image_id = models.ForeignKey(Images, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.type} wound - {self.patient_id.name}"

""" TRACKING RECORDS MODEL """
class TrackingRecords(models.Model):
    tracking_id = models.AutoField(primary_key=True)
    length = models.FloatField()
    width = models.FloatField()
    track_date = models.DateTimeField() 
    exudate_amount = models.CharField(max_length=50)
    exudate_type = models.CharField(max_length=50)
    tissue_type = models.CharField(max_length=50)
    wound_edges = models.CharField(max_length=100, null=True, blank=True)
    skin_around = models.CharField(max_length=100, null=True, blank=True)
    had_a_fever = models.BooleanField(null=True, blank=True)
    pain_level = models.CharField(max_length=20, null=True, blank=True)
    dressing_changer_per_day = models.CharField(max_length=20, null=True, blank=True)
    guidelines_to_patient = models.CharField(max_length=255, null=True, blank=True)
    extra_notes = models.CharField(max_length=255, null=True, blank=True)
    image_id = models.ForeignKey(Images, on_delete=models.SET_NULL, null=True, blank=True)
    wound_id = models.ForeignKey(Wound, on_delete=models.CASCADE, related_name='tracking_records')
    specialist_id = models.ForeignKey(Specialists, on_delete=models.SET_NULL, null=True, blank=True, related_name='tracking_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking Record {self.tracking_id} - {self.track_date}"
    

