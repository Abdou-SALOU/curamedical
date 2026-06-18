from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import whatsapp_inbound, WhatsAppConversationViewSet

router = DefaultRouter()
router.register(r'conversations', WhatsAppConversationViewSet, basename='whatsapp-conversation')

urlpatterns = [
    # Webhook Twilio — sans authentification JWT
    path('inbound/', whatsapp_inbound, name='whatsapp-inbound'),
    # API historique conversations
    path('', include(router.urls)),
]
