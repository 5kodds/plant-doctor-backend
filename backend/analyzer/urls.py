# backend/analyzer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_plant_view, name='analyze_plant'),
]