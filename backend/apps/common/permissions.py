from rest_framework import permissions

class IsDoctor(permissions.BasePermission):
    """
    Permission permettant l'accès uniquement aux médecins.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'doctor')

class IsSecretary(permissions.BasePermission):
    """
    Permission permettant l'accès uniquement au personnel de secrétariat.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'secretary')

class IsDoctorOrSecretary(permissions.BasePermission):
    """
    Permission partagée pour les médecins et le secrétariat.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['doctor', 'secretary']
        )

class IsPatient(permissions.BasePermission):
    """
    Permission permettant l'accès uniquement aux patients.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'patient')
