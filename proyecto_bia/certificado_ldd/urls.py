from django.urls import path
from .views import certificate_view

urlpatterns = [
    path('', certificate_view, name='certificate-web'),
    path('api/certificado/generar/', certificate_view, name='api-generar-certificado'),
]
