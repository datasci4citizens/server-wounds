from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
import os
from django.contrib.auth import get_user_model
from .omop.omop_models import Person, Provider, ConditionOccurrence, ProcedureOccurrence

User = get_user_model()

class PatientNonClinicalInfos(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    accept_tcl = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    bind_code  = models.IntegerField(unique=True, null=True)
    user  = models.ForeignKey(User, models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    print(instance)
    return os.path.join('images', filename)


""" IMAGES MODEL """
class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to=get_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class WoundImage(models.Model):
    wound_image_id = models.AutoField(primary_key=True)
    image = models.ForeignKey(Image, null=True, on_delete=models.DO_NOTHING)
    wound = models.ForeignKey(ConditionOccurrence, on_delete=models.DO_NOTHING)

class TrackingRecordImage(models.Model):
    tracking_record_image_id = models.AutoField(primary_key=True)
    image = models.ForeignKey(Image, null=True, on_delete=models.DO_NOTHING)
    tracking_record = models.ForeignKey(ProcedureOccurrence, on_delete=models.DO_NOTHING) 

class PatientExtraNote(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_extra_notes',
    )

    note_text = models.TextField(
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Nota Extra do Paciente"
        verbose_name_plural = "Notas Extras dos Pacientes"
        ordering = ['-created_at']

    def __str__(self):
        author_name = self.author.username if self.author else 'Anônimo'
        return f"Nota de {author_name} em {self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.note_text[:50]}..."

