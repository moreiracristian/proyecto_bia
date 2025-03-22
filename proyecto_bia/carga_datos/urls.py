from django.urls import path
from . import views

urlpatterns = [
    path('', views.cargar_excel, name='cargar_excel'),
]