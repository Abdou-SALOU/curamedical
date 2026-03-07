from django.urls import path
from .views import (
    PrescriptionListCreateView,
    PrescriptionDetailView,
    download_prescription_pdf
)

urlpatterns = [
    path('', PrescriptionListCreateView.as_view(), name='prescription-list'),
    path('<int:pk>/', PrescriptionDetailView.as_view(), name='prescription-detail'),
    path('<int:pk>/pdf/', download_prescription_pdf, name='prescription-pdf'),
]