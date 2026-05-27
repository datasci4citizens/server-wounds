from django.urls import path, include
from rest_framework import routers
from .views import(
    GoogleLoginView, 
    SpecialistRegistrationView,
    SpecialistPatientListView,
    SpecialistPatientRegisterView,
    PatientsExistsView,
    RegisterPatientComorbidityView,
    UpdateFieldsView,
    MeView,
)
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

router = routers.DefaultRouter()

# Auth endpoints
router.register(r'auth/google', GoogleLoginView, basename='google-login')
router.register(r'auth/register/specialist', SpecialistRegistrationView, basename='specialist-registration')
router.register(r'auth/me', MeView, basename='me')
router.register(r'auth/register/patient', PatientsExistsView, basename="Validate-Patient")


#Provider endpoints
router.register(r'specialist/patients', SpecialistPatientListView, basename='patient_list')
router.register(r'specialist/patient/register', SpecialistPatientRegisterView, basename= 'register_patient')

#Patient endpoints
router.register(r'patient/comorbidities', RegisterPatientComorbidityView, basename='patient-comorbidities')

#other endpoints
router.register(r'Update', UpdateFieldsView, basename="Update Information")

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema', SpectacularAPIView.as_view(), name='schema')
]
