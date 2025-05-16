# Register your models here.
from django.contrib import admin

from .models import Specialists, Patients, Wound, Comorbidities, Images

admin.site.register(Specialists)
admin.site.register(Patients)
admin.site.register(Comorbidities)
admin.site.register(Images)
admin.site.register(Wound)