from rest_framework import serializers
from auditlog.models import LogEntry


FIELD_LABELS = {
    'diagnostic':       'Diagnostic',
    'symptomes':        'Symptômes',
    'notes':            'Notes',
    'examen_clinique':  'Examen clinique',
    'notes_generales':  'Instructions générales',
    'medicament':       'Médicament',
    'statut':           'Statut',
    'date_heure':       'Date/heure',
    'motif':            'Motif',
    'nom':              'Nom',
    'prenom':           'Prénom',
    'email':            'Email',
    'telephone':        'Téléphone',
    'role':             'Rôle',
    'is_active':        'Actif',
    'password':         'Mot de passe',
    'groupe_sanguin':   'Groupe sanguin',
}

CONTENT_TYPE_ICONS = {
    'prescription': '💊',
    'consultation': '🩺',
    'rendez':       '📅',
    'patient':      '👤',
    'user':         '🔐',
}


class LogEntrySerializer(serializers.ModelSerializer):
    actor_name      = serializers.SerializerMethodField()
    actor_role      = serializers.SerializerMethodField()
    module          = serializers.SerializerMethodField()
    module_icon     = serializers.SerializerMethodField()
    action_label    = serializers.SerializerMethodField()
    changes_summary = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = [
            'id', 'timestamp',
            'actor_name', 'actor_role',
            'action', 'action_label',
            'object_repr',
            'module', 'module_icon',
            'changes_summary',
            'remote_addr',
        ]

    def _fallback_actor(self, obj):
        """Si actor=None, essaie de retrouver l'auteur réel depuis les données
        sérialisées (medecin pour les consultations/prescriptions/RDV, ou
        utilisateur lié pour un Patient auto-inscrit)."""
        from .models import User
        try:
            data = obj.changes or {}
        except Exception:
            data = {}

        # 1. Champ 'medecin' présent dans les changes → c'est l'auteur
        medecin_change = data.get('medecin')
        if isinstance(medecin_change, list) and len(medecin_change) == 2:
            medecin_id = medecin_change[1] or medecin_change[0]
            if medecin_id:
                try:
                    return User.objects.get(pk=medecin_id)
                except (User.DoesNotExist, ValueError, TypeError):
                    pass

        # 2. Patient avec champ 'utilisateur' → c'est lui-même (auto-inscription)
        utilisateur_change = data.get('utilisateur')
        if isinstance(utilisateur_change, list) and len(utilisateur_change) == 2:
            user_id = utilisateur_change[1] or utilisateur_change[0]
            if user_id:
                try:
                    return User.objects.get(pk=user_id)
                except (User.DoesNotExist, ValueError, TypeError):
                    pass
        return None

    def get_actor_name(self, obj):
        actor = obj.actor or self._fallback_actor(obj)
        if actor:
            full = actor.get_full_name()
            return full if full.strip() else actor.username
        return 'Système'

    def get_actor_role(self, obj):
        actor = obj.actor or self._fallback_actor(obj)
        if actor:
            role = getattr(actor, 'role', '')
            return {
                'administrateur': 'Administrateur',
                'medecin':        'Médecin',
                'secretaire':     'Secrétaire',
                'patient':        'Patient',
            }.get(role, role.capitalize() if role else '')
        return ''

    def get_module(self, obj):
        ct = str(obj.content_type) if obj.content_type else ''
        if '|' in ct:
            return ct.split('|')[-1].strip()
        return ct

    def get_module_icon(self, obj):
        ct = str(obj.content_type).lower() if obj.content_type else ''
        for key, icon in CONTENT_TYPE_ICONS.items():
            if key in ct:
                return icon
        return '📋'

    def get_action_label(self, obj):
        return {0: 'Création', 1: 'Modification', 2: 'Suppression'}.get(obj.action, str(obj.action))

    def get_changes_summary(self, obj):
        """Retourne les champs modifiés pertinents en langage naturel."""
        try:
            changes = obj.changes or {}
        except Exception:
            return []

        SKIP = {'id', 'cree_le', 'modifie_le', 'date_consultation', 'password',
                'suggestions_ia', 'serialized_data', 'ia_utilisee', 'lignes'}

        summary = []
        for field, values in changes.items():
            if field in SKIP:
                continue
            label = FIELD_LABELS.get(field, field.replace('_', ' ').capitalize())
            if isinstance(values, list) and len(values) == 2:
                old, new = values
                if old in (None, 'None', '') and new not in (None, 'None', ''):
                    if field == 'diagnostic':
                        summary.append(f"Diagnostic : {new}")
                    elif field == 'statut':
                        summary.append(f"Statut → {new}")
                    elif field not in ('medecin', 'patient', 'consultation', 'rendez_vous'):
                        if new and str(new).strip():
                            summary.append(f"{label} renseigné")
                elif old not in (None, 'None', '') and new not in (None, 'None', '') and old != new:
                    if field == 'diagnostic':
                        summary.append(f"Diagnostic : {old} → {new}")
                    elif field == 'statut':
                        summary.append(f"Statut : {old} → {new}")
                    elif field not in ('medecin', 'patient', 'consultation', 'rendez_vous'):
                        summary.append(f"{label} modifié")
        return summary[:4]
