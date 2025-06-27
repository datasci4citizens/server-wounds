from django.db import models
from django.utils import timezone
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

class TextoRecebido(models.Model):
    conteudo = models.TextField(max_length=2000)
    data_recebimento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Texto de {self.data_recebimento.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Texto Recebido"
        verbose_name_plural = "Textos Recebidos"
        ordering = ['-data_recebimento']