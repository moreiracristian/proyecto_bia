from django.urls import path
from . import views

urlpatterns = [
    path('', views.cargar_excel, name='cargar_excel'),  # Vista principal
    path('confirmar/', views.confirmar_carga, name='confirmar_carga'),  # Confirmación con vista previa
    path('errores/', views.errores_validacion, name='errores_validacion'),  # Lista y exportación de errores
]