from django.urls import include, path

from . import views

urlpatterns = [
    path('about/app_cicatrizando/', views.index, name="index"),
]