from django.urls import path
from . import views

app_name = 'therapists'

urlpatterns = [
    path('therapists/', views.frontend),
    path('therapists/<id>/', views.frontend),
]
