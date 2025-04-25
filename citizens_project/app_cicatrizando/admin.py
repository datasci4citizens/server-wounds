# Register your models here.
from django.contrib import admin

from .models import Specialists, Patients, Measurement, Comorbidities, Images

admin.site.register(Specialists)
admin.site.register(Patients)
admin.site.register(Measurement)
admin.site.register(Comorbidities)
admin.site.register(Images)