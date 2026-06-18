from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Patient
from .serializers import PatientSerializer, PatientListSerializer
from apps.users.permissions import (
    EstMedecinOuSecretaire,
    EstProprietaire
)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.filter(est_archive=False)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['groupe_sanguin', 'sexe', 'ville']
    search_fields = ['nom', 'prenom', 'cin', 'telephone']
    ordering_fields = ['nom', 'prenom', 'cree_le']
    ordering = ['nom']

    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer

    def get_permissions(self):
        if self.action in ['mes_infos', 'list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [EstMedecinOuSecretaire()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Patient.objects.filter(utilisateur=user)
        if user.role == 'medecin':
            from django.db import models
            return Patient.objects.filter(
                models.Q(rendez_vous__medecin=user) |
                models.Q(consultations__medecin=user)
            ).distinct()
        if user.role == 'secretaire':
            return Patient.objects.all()
        # Administrateur : aucun accès aux données médicales
        return Patient.objects.none()

    @action(detail=True, methods=['patch'], url_path='archiver')
    def archiver(self, request, pk=None):
        """Archive un patient au lieu de le supprimer."""
        patient = self.get_object()
        patient.est_archive = True
        patient.save()
        return Response({'detail': f'Patient {patient.nom_complet} archivé.'})

    @action(
        detail=False,
        methods=['get'],
        url_path='archives',
        permission_classes=[EstMedecinOuSecretaire]
    )
    def archives(self, request):
        """Liste les patients archivés — médecin et secrétaire uniquement."""
        patients = Patient.objects.filter(est_archive=True).order_by('nom', 'prenom')
        recherche = request.query_params.get('search', '').strip()
        if recherche:
            from django.db import models
            patients = patients.filter(
                models.Q(nom__icontains=recherche) |
                models.Q(prenom__icontains=recherche) |
                models.Q(cin__icontains=recherche)
            )
        page = self.paginate_queryset(patients)
        if page is not None:
            serializer = PatientListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PatientListSerializer(patients, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'patch'],
        url_path='restaurer',
        permission_classes=[EstMedecinOuSecretaire]
    )
    def restaurer(self, request, pk=None):
        """Restaure un patient archivé."""
        patient = Patient.objects.filter(pk=pk, est_archive=True).first()
        if not patient:
            return Response(
                {'detail': 'Patient introuvable dans les archives.'},
                status=status.HTTP_404_NOT_FOUND
            )
        patient.est_archive = False
        patient.save(update_fields=['est_archive'])
        return Response({'detail': f'Patient {patient.nom_complet} restauré.'})

    @action(
        detail=False,
        methods=['get'],
        url_path='mes-infos',
        permission_classes=[permissions.IsAuthenticated]
    )
    def mes_infos(self, request):
        """Un patient connecté consulte son propre dossier."""
        try:
            patient = Patient.objects.get(utilisateur=request.user)
            serializer = PatientSerializer(patient)
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response(
                {'detail': 'Aucun dossier patient trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=False,
        methods=['get'],
        url_path='stats',
        permission_classes=[EstMedecinOuSecretaire]
    )
    def stats(self, request):
        """Stats patients pour le dashboard."""
        maintenant = timezone.now()
        return Response({
            'total': Patient.objects.filter(est_archive=False).count(),
            'archives': Patient.objects.filter(est_archive=True).count(),
            'nouveaux_ce_mois': Patient.objects.filter(
                est_archive=False,
                cree_le__month=maintenant.month,
                cree_le__year=maintenant.year
            ).count(),
        })
