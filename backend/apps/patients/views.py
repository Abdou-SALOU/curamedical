from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import Patient
from .serializers import PatientSerializer, PatientListSerializer
from apps.users.permissions import IsDoctorOrAdmin, IsSecretaryOrAdmin

class PatientListCreateView(generics.ListCreateAPIView):
    # Médecins, secrétaires et admins peuvent accéder
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Patient.objects.filter(is_archived=False)
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
    permission_classes = [permissions.IsAuthenticated]

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