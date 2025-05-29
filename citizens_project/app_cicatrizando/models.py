from django.db import models
from django.utils import timezone
import uuid
import os
from .omop.omop_models import Person

class PatientNonClinicalInfos(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    accept_tcl = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
