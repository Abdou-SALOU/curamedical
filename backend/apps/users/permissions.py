from rest_framework import permissions


class EstMedecin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'medecin'


class EstSecretaire(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'secretaire'


class EstAdministrateur(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.role == 'administrateur' or request.user.is_superuser)
        )


class EstPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'patient'


class EstMedecinOuSecretaire(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['medecin', 'secretaire']
        )


class EstStaffOuAdministrateur(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['medecin', 'secretaire', 'administrateur']
        )


class EstProprietaire(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'utilisateur'):
            return obj.utilisateur == request.user
        if hasattr(obj, 'patient') and hasattr(obj.patient, 'utilisateur'):
            return obj.patient.utilisateur == request.user
        if hasattr(obj, 'consultation') and hasattr(obj.consultation, 'patient'):
            return obj.consultation.patient.utilisateur == request.user
        return False
