# Register your models here.
from django.contrib import admin
from .models import Specialists, Comorbidities, Patients, Images, Wound, TrackingRecords

# Register original models
admin.site.register(Specialists)
admin.site.register(Comorbidities)
admin.site.register(Patients)
admin.site.register(Images)
admin.site.register(Wound)
admin.site.register(TrackingRecords)

# Register OMOP models - import inside a try/except block to avoid issues during app loading
try:
    from .models_omop import Person, Provider, ConditionConcept, ConditionOccurrence, \
        NoteAttachment, Observation, Measurement
        
    admin.site.register(Person)
    admin.site.register(Provider)
    admin.site.register(ConditionConcept)
    admin.site.register(ConditionOccurrence)
    admin.site.register(NoteAttachment)
    admin.site.register(Observation)
    admin.site.register(Measurement)
except:
    # If models can't be imported during the first app load, they'll be registered later
    pass