from django.db import models
from django.utils import timezone
import uuid
import os
from django.contrib.auth import get_user_model
from .omop.omop_models import Person, Provider

User = get_user_model()

class PatientNonClinicalInfos(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    accept_tcl = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SpecialistNonOmopInfos(models.Model):
    provider = models.ForeignKey(Provider, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    updated_at = models.DateTimeField(auto_now=True)
