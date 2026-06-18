from rest_framework import permissions


class IsDoctor(permissions.BasePermission):
    """Autorise uniquement les médecins."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'medecin'
        )


class IsSecretary(permissions.BasePermission):
    """Autorise uniquement les secrétaires."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'secretaire'
        )


class IsAdmin(permissions.BasePermission):
    """Autorise uniquement les administrateurs."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'administrateur' or request.user.is_superuser)
        )


class IsDoctorOrAdmin(permissions.BasePermission):
    """Autorise les médecins et les administrateurs."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ['medecin', 'administrateur']
        )


class IsSecretaryOrAdmin(permissions.BasePermission):
    """Autorise les secrétaires et les administrateurs."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ['secretaire', 'administrateur']
        )


class IsDoctorOrSecretary(permissions.BasePermission):
    """Autorise les médecins, secrétaires et administrateurs."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role in ['medecin', 'secretaire', 'administrateur'] or request.user.is_superuser)
        )


class IsPatient(permissions.BasePermission):
    """Autorise uniquement les patients."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'patient'
        )


class ReadOnly(permissions.BasePermission):
    """Autorise uniquement les requêtes en lecture."""
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']
