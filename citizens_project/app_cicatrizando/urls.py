from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from .views import(
    GoogleLoginView, 
    SpecialistRegistrationView,
    SpecialistPatientListView,
    SpecialistPatientRegisterView,
    SpecialistPatientUpdateView,
    PatientValidationView,
    PatientMeView,
    MeView,
    RegisterPatientComorbidityView,
    ComorbiditySearchView,
    UpdateFieldsView,
    WoundViewSet
)
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

router = routers.DefaultRouter()

# Auth endpoints
router.register(r'auth/google', GoogleLoginView, basename='google-login')
router.register(r'auth/register/specialist', SpecialistRegistrationView, basename='specialist-registration')
router.register(r'auth/me', MeView, basename='me')
router.register(r'patient/me', PatientMeView, basename='patient-me')
router.register(r'patient/validation', PatientValidationView, basename="Patient-Validation")


# specialist endpoints
router.register(r'specialist/patients', SpecialistPatientListView, basename='patient_list')
router.register(r'specialist/patient/register', SpecialistPatientRegisterView, basename= 'register_patient')
router.register(r'specialist/patient/update', SpecialistPatientUpdateView, basename='update_patient')
router.register(r'patient/comorbidities', RegisterPatientComorbidityView, basename='patient-comorbidities')
router.register(r'comorbidities/search', ComorbiditySearchView, basename='comorbidities-search')
router.register(r'wounds', WoundViewSet, basename='wounds')

urlpatterns = [
    path('', include(router.urls)),
    path('Update/', UpdateFieldsView.as_view({'patch': 'patch'}), name="Update Information"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema', SpectacularAPIView.as_view(), name='schema')
]
