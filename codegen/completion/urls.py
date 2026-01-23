from django.urls import path
from . import views

urlpatterns = [
    path('completion', views.completion, name='completion'),
]