from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer
from apps.users.permissions import IsDoctorOrAdmin

class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Appointment.objects.select_related('patient', 'doctor')

        doctor_id = self.request.query_params.get('doctor')
        date = self.request.query_params.get('date')
        status = self.request.query_params.get('status')
        patient_id = self.request.query_params.get('patient')

        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if date:
            queryset = queryset.filter(scheduled_at__date=date)
        if status:
            queryset = queryset.filter(status=status)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        return queryset

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        # Seuls médecins et admins peuvent supprimer
        if request.user.role not in ['doctor', 'admin']:
            return Response(
                {'error': 'Seul un médecin peut supprimer un rendez-vous'},
                status=403
            )
        return super().destroy(request, *args, **kwargs)