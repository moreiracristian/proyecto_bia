from django.urls import path
from . import views

urlpatterns = [
    # Vistas clásicas
    path('', views.cargar_excel, name='cargar_excel'),
    path('confirmar/', views.confirmar_carga, name='confirmar_carga'),
    path('errores/', views.errores_validacion, name='errores_validacion'),

    # API para React
    path('api/', views.api_cargar_excel, name='api_cargar_excel'),
    path('api/confirmar/', views.api_confirmar_carga, name='api_confirmar_carga'),
    path('api/errores/', views.api_errores_validacion, name='api_errores_validacion'),
]