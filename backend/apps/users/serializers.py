from rest_framework import serializers
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class FlexTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Accepte username OU email dans le champ 'username'."""
    def validate(self, attrs):
        login = attrs.get('username', '').strip()
        if '@' in login:
            try:
                user = User.objects.get(email__iexact=login)
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    # Statut de validation du dossier patient lié (null pour le staff).
    # Permet au frontend d'afficher la bannière « en attente de validation ».
    patient_statut = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name',
            'role', 'telephone', 'specialite', 'is_staff',
            'patient_statut',
        )
        read_only_fields = ('is_staff',)
        extra_kwargs = {
            'password': {'write_only': True}  # jamais exposé dans les réponses
        }

    def get_patient_statut(self, obj):
        if obj.role != 'patient':
            return None
        patient = getattr(obj, 'patient_profile', None)
        return patient.statut_validation if patient else None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'password', 'password_confirm',
            'first_name', 'last_name',
            'role', 'telephone', 'specialite'
        )

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Les mots de passe ne correspondent pas."
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la modification — pas de changement de mot de passe ici."""
    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name',
            'role', 'telephone', 'specialite'
        )


class PatientRegisterSerializer(serializers.ModelSerializer):
    """Sérialiseur d'auto-inscription pour les patients."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    # Champs du profil Patient
    date_naissance = serializers.DateField(write_only=True)
    sexe = serializers.ChoiceField(choices=[('M', 'Masculin'), ('F', 'Féminin')], write_only=True)
    cin = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'password', 'password_confirm',
            'first_name', 'last_name',
            'telephone',
            'date_naissance', 'sexe', 'cin',
        )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value

    def validate_cin(self, value):
        if value:
            from apps.patients.models import Patient
            if Patient.objects.filter(cin=value).exists():
                raise serializers.ValidationError("Ce numéro CIN est déjà utilisé.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Les mots de passe ne correspondent pas."
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        # Extraire les champs Patient
        date_naissance = validated_data.pop('date_naissance')
        sexe = validated_data.pop('sexe')
        cin = validated_data.pop('cin', '')
        validated_data.pop('password_confirm')

        # Créer le User avec role=patient
        user = User.objects.create_user(
            role='patient',
            **validated_data
        )

        # Importer ici pour éviter les imports circulaires
        from apps.patients.models import Patient
        from auditlog.context import set_actor

        # Attribuer l'audit log au nouvel utilisateur lui-même
        # (auto-inscription : pas de request.user authentifié)
        request = self.context.get('request')
        remote_addr = request.META.get('REMOTE_ADDR') if request else None
        with set_actor(user, remote_addr=remote_addr):
            Patient.objects.create(
                utilisateur=user,
                nom=user.last_name or user.username,
                prenom=user.first_name or '',
                date_naissance=date_naissance,
                sexe=sexe,
                cin=cin or None,
                telephone=user.telephone or '',
                email=user.email or '',
                # Auto-inscription : le dossier reste à valider par le secrétariat.
                statut_validation='EN_ATTENTE',
            )
        return user
