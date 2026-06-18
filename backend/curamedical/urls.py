from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.users.views import AuditLogViewSet
from apps.users.serializers import FlexTokenObtainPairSerializer


class FlexTokenObtainPairView(TokenObtainPairView):
    serializer_class = FlexTokenObtainPairSerializer

router = DefaultRouter()
router.register(r'api/auditlog', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Authentification JWT ───────────────────────────────────
    path('api/token/',         FlexTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # ── Applications ───────────────────────────────────────────
    path('api/users/',         include('apps.users.urls')),
    path('api/patients/',      include('apps.patients.urls')),
    path('api/appointments/',  include('apps.appointments.urls')),
    path('api/consultations/', include('apps.consultations.urls')),
    path('api/prescriptions/', include('apps.prescriptions.urls')),
    path('api/chat/',          include('apps.chat.urls')),
    path('api/whatsapp/',      include('apps.whatsapp.urls')),
    path('',                   include(router.urls)),

    # ── Documentation API (Swagger / OpenAPI) ──────────────────
    path('api/schema/', SpectacularAPIView.as_view(),         name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Servir les fichiers media en développement (DEBUG=True)
# En production, nginx/S3 prend le relais
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
