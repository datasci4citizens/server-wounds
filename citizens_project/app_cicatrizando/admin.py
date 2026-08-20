from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import Comorbidity, WoundsUser, Provider, Patient, Wound, Observation

class WoundInline(TabularInline):
    model = Wound
    extra = 0
    fields = ('etiology', 'location', 'is_healed', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True
    tab = True

class ObservationInline(StackedInline):
    model = Observation
    extra = 0
    fields = (
        'author', 'created_at', 'pain_level', 'exudate_amount', 
        'tissue_type', 'fever_24h'
    )
    readonly_fields = ('created_at',)
    show_change_link = True
    tab = True

@admin.register(Comorbidity)
class ComorbidityAdmin(ModelAdmin):
    list_display = ('name', 'concept_id', 'code')
    search_fields = ('name', 'concept_id', 'code')

@admin.register(WoundsUser)
class WoundsUserAdmin(ModelAdmin):
    list_display = ('user_name', 'role', 'city', 'state', 'created_at')
    list_filter = ('role', 'state')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'city')
    readonly_fields = ('created_at', 'updated_at')
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.username})"
    user_name.short_description = "User"

@admin.register(Provider)
class ProviderAdmin(ModelAdmin):
    list_display = ('get_name', 'professional_id', 'contact_email', 'contact_phone')
    search_fields = ('professional_id', 'contact_email', 'contact_phone', 'wounds_user__user__username', 'wounds_user__user__first_name')
    autocomplete_fields = ('wounds_user',)

    def get_name(self, obj):
        return f"{obj.wounds_user.user.first_name} {obj.wounds_user.user.last_name}"
    get_name.short_description = "Provider Name"

@admin.register(Patient)
class PatientAdmin(ModelAdmin):
    list_display = ('get_name', 'gender', 'smoking_status', 'contact_email', 'contact_phone')
    list_filter = ('gender', 'smoking_status')
    search_fields = ('wounds_user__user__username', 'wounds_user__user__first_name', 'wounds_user__user__last_name', 'contact_email')
    autocomplete_fields = ('wounds_user',)
    filter_horizontal = ('assigned_providers', 'comorbidities')
    inlines = [WoundInline]

    fieldsets = (
        ('Informações de Usuário', {
            'fields': ('wounds_user', 'contact_email', 'contact_phone')
        }),
        ('Perfil de Saúde', {
            'fields': ('gender', 'height', 'weight', 'smoking_status', 'alcohol_consumption')
        }),
        ('Relações Clínicas', {
            'fields': ('assigned_providers', 'comorbidities')
        }),
    )

    def get_name(self, obj):
        return f"{obj.wounds_user.user.first_name} {obj.wounds_user.user.last_name}"
    get_name.short_description = "Patient Name"

@admin.register(Wound)
class WoundAdmin(ModelAdmin):
    list_display = ('patient_name', 'etiology', 'location', 'is_healed', 'created_at')
    list_filter = ('is_healed', 'etiology', 'location')
    search_fields = ('patient__wounds_user__user__username', 'patient__wounds_user__user__first_name')
    autocomplete_fields = ('patient',)
    readonly_fields = ('created_at',)
    inlines = [ObservationInline]
    
    def patient_name(self, obj):
        return f"{obj.patient.wounds_user.user.first_name} {obj.patient.wounds_user.user.last_name}"
    patient_name.short_description = "Patient"

@admin.register(Observation)
class ObservationAdmin(ModelAdmin):
    list_display = ('wound', 'author_name', 'created_at', 'pain_level', 'exudate_amount', 'tissue_type', 'fever_24h')
    list_filter = ('fever_24h', 'exudate_amount', 'tissue_type', 'periwound_skin')
    search_fields = ('wound__patient__wounds_user__user__username', 'author__user__username', 'author__user__first_name')
    autocomplete_fields = ('wound', 'author')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identificação', {
            'fields': ('wound', 'author', 'created_at')
        }),
        ('Métricas Clínicas', {
            'fields': ('pain_level', 'exudate_amount', 'exudate_type', 'tissue_type', 'dressing_changes', 'periwound_skin', 'wound_edge', 'fever_24h')
        }),
        ('Anotações e Mídia', {
            'fields': ('extra_notes', 'patient_guidelines', 'image')
        }),
    )

    def author_name(self, obj):
        if obj.author:
            return f"{obj.author.user.first_name} {obj.author.user.last_name}"
        return "-"
    author_name.short_description = "Author"
