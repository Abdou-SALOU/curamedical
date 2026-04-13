from rest_framework import generics, permissions, exceptions
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer
from apps.common.permissions import IsDoctorOrSecretary

class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'patient':
            # Force le profil patient de l'utilisateur connecté
            if not hasattr(user, 'patient_profile'):
               raise exceptions.PermissionDenied("Profil patient inexistant")
            serializer.save(patient=user.patient_profile)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor')

        # Si l'utilisateur est un patient, il ne voit que ses rendez-vous
        if user.role == 'patient':
            if hasattr(user, 'patient_profile'):
                queryset = queryset.filter(patient=user.patient_profile)
            else:
                return Appointment.objects.none()

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
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsDoctorOrSecretary()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == 'patient':
            if not hasattr(user, 'patient_profile') or obj.patient != user.patient_profile:
                raise exceptions.PermissionDenied("Vous ne pouvez accéder qu'à vos propres rendez-vous.")
        return obj

    def destroy(self, request, *args, **kwargs):
        # Seuls médecins et admins peuvent supprimer
        if request.user.role not in ['doctor', 'admin']:
            return Response(
                {'error': 'Seul un médecin peut supprimer un rendez-vous'},
                status=403
            )
        return super().destroy(request, *args, **kwargs)