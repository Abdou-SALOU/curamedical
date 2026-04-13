from django.urls import path
from .views import (
    ConsultationListCreateView,
    ConsultationDetailView,
    get_ia_suggestions,
    download_consultation_report_pdf
)

urlpatterns = [
    path('', ConsultationListCreateView.as_view(), name='consultation-list'),
    path('<int:pk>/', ConsultationDetailView.as_view(), name='consultation-detail'),
    path('<int:pk>/report/', download_consultation_report_pdf, name='consultation-report'),
    path('ia/suggest/', get_ia_suggestions, name='ia-suggest'),
]