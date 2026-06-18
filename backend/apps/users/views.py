from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, PatientRegisterSerializer
from .audit_serializers import LogEntrySerializer
from auditlog.models import LogEntry
from .permissions import EstAdministrateur, EstStaffOuAdministrateur


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'register':
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [EstAdministrateur()]
        if self.action == 'list':
            return [EstStaffOuAdministrateur()]
        if self.action == 'retrieve':
            return [EstStaffOuAdministrateur()]
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        if self.action == 'medecins':
            return [permissions.IsAuthenticated()]
        if self.action == 'changer_mot_de_passe':
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [EstAdministrateur()]
        return [EstAdministrateur()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'administrateur' or user.is_superuser:
            return User.objects.all()
        if user.role in ['medecin', 'secretaire']:
            return User.objects.filter(
                role__in=['medecin', 'secretaire']
            )
        # patient ne voit que lui-même
        return User.objects.filter(pk=user.pk)

    @action(
        detail=False,
        methods=['post'],
        url_path='register',
        permission_classes=[permissions.AllowAny]
    )
    def register(self, request):
        """Auto-inscription d'un patient depuis le site public."""
        serializer = PatientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'detail': 'Compte créé avec succès. Vous pouvez maintenant vous connecter.',
                    'username': user.username,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Retourne le profil de l'utilisateur connecté."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='medecins',
        permission_classes=[permissions.IsAuthenticated]
    )
    def medecins(self, request):
        """Liste des médecins actifs — pour le formulaire de RDV."""
        medecins = User.objects.filter(role='medecin', is_active=True)
        serializer = UserSerializer(medecins, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        url_path='changer-mot-de-passe',
        permission_classes=[permissions.IsAuthenticated]
    )
    def changer_mot_de_passe(self, request, pk=None):
        """Seul l'utilisateur lui-même ou l'admin peut changer le mot de passe."""
        user = self.get_object()

        if request.user != user and not request.user.est_administrateur:
            return Response(
                {'detail': 'Non autorisé.'},
                status=status.HTTP_403_FORBIDDEN
            )

        ancien = request.data.get('ancien_mot_de_passe')
        nouveau = request.data.get('nouveau_mot_de_passe')

        if not ancien or not nouveau:
            return Response(
                {'detail': 'Les deux champs sont requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(ancien):
            return Response(
                {'detail': 'Ancien mot de passe incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(nouveau) < 8:
            return Response(
                {'detail': 'Le nouveau mot de passe doit contenir au moins 8 caractères.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(nouveau)
        user.save()
        return Response({'detail': 'Mot de passe mis à jour avec succès.'})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les journaux d'audit — réservé aux admins."""
    queryset = LogEntry.objects.select_related('actor', 'content_type').all()
    serializer_class = LogEntrySerializer
    permission_classes = [EstAdministrateur]
    # search_fields = ['object_repr', 'actor__username', 'actor__first_name', 'actor__last_name']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
