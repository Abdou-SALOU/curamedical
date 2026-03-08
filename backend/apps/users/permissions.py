from rest_framework.permissions import BasePermission

class IsDoctor(BasePermission):
    """Autorise uniquement les médecins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'doctor'

class IsSecretary(BasePermission):
    """Autorise uniquement les secrétaires"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'secretary'

class IsAdmin(BasePermission):
    """Autorise uniquement les administrateurs"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsDoctorOrAdmin(BasePermission):
    """Autorise les médecins et les administrateurs"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['doctor', 'admin']

class IsSecretaryOrAdmin(BasePermission):
    """Autorise les secrétaires et les administrateurs"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['secretary', 'admin']

class ReadOnly(BasePermission):
    """Autorise uniquement les requêtes en lecture"""
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']