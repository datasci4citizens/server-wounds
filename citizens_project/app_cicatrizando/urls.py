from django.urls import include, path

from . import views

# from django_scalar.views import scalar_viewer
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from app_cicatrizando.scalar import scalar_viewer


urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger", SpectacularSwaggerView.as_view(), name="schema-swagger-ui"),
    path("api/schema/scalar", scalar_viewer, name="schema-scalar-ui"), 
    path('about/app_cicatrizando/', views.index, name="index"),
]