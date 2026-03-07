from django.urls import path
from .views import (
    ConsultationListCreateView,
    ConsultationDetailView,
    get_ia_suggestions
)

urlpatterns = [
    path('', ConsultationListCreateView.as_view(), name='consultation-list'),
    path('<int:pk>/', ConsultationDetailView.as_view(), name='consultation-detail'),
    path('ia/suggest/', get_ia_suggestions, name='ia-suggest'),
]