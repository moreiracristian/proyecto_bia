from django.urls import path
from .views import certificate_view

urlpatterns = [
    path('', certificate_view, name='certificate'),
]
