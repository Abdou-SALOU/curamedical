from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Prescription
from .serializers import PrescriptionSerializer
from .pdf_generator import generate_prescription_pdf
from apps.users.permissions import IsDoctorOrAdmin


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctorOrAdmin]  # ← Secrétaire bloquée

    def get_queryset(self):
        return Prescription.objects.select_related(
            'consultation__appointment__patient',
            'consultation__doctor'
        )


class PrescriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctorOrAdmin]  # ← Secrétaire bloquée


@api_view(['GET'])
@permission_classes([IsDoctorOrAdmin])  # ← Secrétaire bloquée
def download_prescription_pdf(request, pk):
    try:
        prescription = Prescription.objects.select_related(
            'consultation__appointment__patient',
            'consultation__doctor'
        ).get(pk=pk)
    except Prescription.DoesNotExist:
        return Response({'error': 'Ordonnance introuvable'}, status=404)

    pdf_buffer = generate_prescription_pdf(prescription)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="ordonnance_{prescription.id}.pdf"'
    )
    return response