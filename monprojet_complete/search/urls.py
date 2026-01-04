"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from . import views

from apps.groups.models import Groupe
app_name = 'search'  # This registers the namespace "search"

urlpatterns = [
    path('', views.search_results, name='results'),
]

