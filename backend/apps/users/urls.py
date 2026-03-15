from django.urls import path
from .views import MeView, UserListCreateView, UserDetailView, DoctorListView

urlpatterns = [
    path('me/', MeView.as_view(), name='user-me'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('', UserListCreateView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]