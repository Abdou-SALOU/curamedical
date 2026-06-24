from rest_framework import serializers
from .models import Patient


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les listes et les relations."""
    age = serializers.ReadOnlyField()
    nom_complet = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = (
            'id', 'utilisateur', 'nom', 'prenom', 'nom_complet',
            'date_naissance', 'age', 'sexe', 'telephone', 'adresse',
            'groupe_sanguin', 'est_archive', 'cin', 'modifie_le',
            'statut_validation', 'cree_le', 'email'
        )


class PatientSerializer(serializers.ModelSerializer):
    """Serializer complet pour le dossier patient."""
    age = serializers.ReadOnlyField()
    nom_complet = serializers.ReadOnlyField()
    # Champ déclaré explicitement → pas de UniqueValidator auto (basé sur le numéro
    # brut). L'unicité est vérifiée par validate_telephone APRÈS normalisation,
    # pour un message cohérent quel que soit le format saisi.
    telephone = serializers.CharField(max_length=20)

    class Meta:
        model = Patient
        fields = (
            'id', 'utilisateur',
            'nom', 'prenom', 'nom_complet',
            'date_naissance', 'age', 'sexe', 'cin',
            'telephone', 'email', 'adresse', 'ville',
            'groupe_sanguin', 'allergies',
            'antecedents_medicaux', 'medicaments_en_cours',
            'est_archive', 'statut_validation', 'cree_le', 'modifie_le'
        )
        read_only_fields = ('id', 'statut_validation', 'cree_le', 'modifie_le')

    def validate_cin(self, value):
        """CIN unique — vérifie qu'il n'existe pas déjà."""
        qs = Patient.objects.filter(cin=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Un patient avec ce CIN existe déjà.")
        return value

    def validate_telephone(self, value):
        """Numéro normalisé en E.164 + unicité (évite qu'un même numéro pointe
        vers plusieurs dossiers — source de confusion sur les documents WhatsApp).
        """
        from apps.common.phone import normalize_phone
        value = normalize_phone(value)
        qs = Patient.objects.filter(telephone=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Un patient avec ce numéro de téléphone existe déjà."
            )
        return value
