from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RendezVousViewSet

router = DefaultRouter()
router.register(r'', RendezVousViewSet, basename='rendez-vous')

urlpatterns = [
    path('', include(router.urls)),
]
