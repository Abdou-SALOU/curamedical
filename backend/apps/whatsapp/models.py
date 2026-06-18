from django.db import models


class WhatsAppConversation(models.Model):
    phone_number = models.CharField(
        'Numéro de téléphone', max_length=30, unique=True, db_index=True
    )
    patient = models.ForeignKey(
        'patients.Patient',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='whatsapp_conversations',
        verbose_name='Patient',
    )
    # State machine pour les flux multi-tours (RDV, sélection ordonnance…)
    state = models.CharField('État', max_length=50, default='idle')
    state_data = models.JSONField('Données d\'état', default=dict, blank=True)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Mis à jour le', auto_now=True)

    class Meta:
        verbose_name = 'Conversation WhatsApp'
        verbose_name_plural = 'Conversations WhatsApp'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.phone_number} — {self.patient or 'Patient inconnu'}"


class WhatsAppMessage(models.Model):
    INBOUND = 'inbound'
    OUTBOUND = 'outbound'
    DIRECTION_CHOICES = [(INBOUND, 'Entrant'), (OUTBOUND, 'Sortant')]

    conversation = models.ForeignKey(
        WhatsAppConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Conversation',
    )
    direction = models.CharField('Direction', max_length=10, choices=DIRECTION_CHOICES)
    body = models.TextField('Corps du message')
    media_url = models.URLField('URL du média', blank=True, null=True)
    twilio_sid = models.CharField('SID Twilio', max_length=60, blank=True)
    sent_at = models.DateTimeField('Envoyé le', auto_now_add=True)

    class Meta:
        verbose_name = 'Message WhatsApp'
        verbose_name_plural = 'Messages WhatsApp'
        ordering = ['sent_at']

    def __str__(self):
        return f"[{self.direction}] {self.body[:60]}"
