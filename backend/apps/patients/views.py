from rest_framework import generics, permissions, exceptions
from rest_framework.response import Response
from django.db.models import Q
from .models import Patient
from .serializers import PatientSerializer, PatientListSerializer
from apps.common.permissions import IsDoctorOrSecretary

class PatientListCreateView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsDoctorOrSecretary()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Patient.objects.filter(is_archived=False)

        # Si l'utilisateur est un patient, il ne voit que son profil
        if user.role == 'patient':
            if hasattr(user, 'patient_profile'):
                queryset = queryset.filter(id=user.patient_profile.id)
            else:
                return Patient.objects.none()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(national_id__icontains=search)
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PatientListSerializer
        return PatientSerializer

class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsDoctorOrSecretary()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == 'patient':
            if not hasattr(user, 'patient_profile') or obj != user.patient_profile:
                raise exceptions.PermissionDenied("Accès interdit")
        return obj

    def destroy(self, request, *args, **kwargs):
        # Seule la secrétaire et l'admin peuvent archiver
        if request.user.role not in ['secretary', 'admin', 'doctor']:
            return Response(
                {'error': 'Permission refusée'},
                status=403
            )
        patient = self.get_object()
        patient.is_archived = True
        patient.save()
        return Response({'message': 'Patient archivé avec succès'})