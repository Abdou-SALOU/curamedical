import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(
                    db_index=True, max_length=30, unique=True,
                    verbose_name='Numéro de téléphone'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Mis à jour le')),
                ('patient', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='whatsapp_conversations',
                    to='patients.patient',
                    verbose_name='Patient',
                )),
            ],
            options={
                'verbose_name': 'Conversation WhatsApp',
                'verbose_name_plural': 'Conversations WhatsApp',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='WhatsAppMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(
                    choices=[('inbound', 'Entrant'), ('outbound', 'Sortant')],
                    max_length=10,
                    verbose_name='Direction',
                )),
                ('body', models.TextField(verbose_name='Corps du message')),
                ('media_url', models.URLField(blank=True, null=True, verbose_name='URL du média')),
                ('twilio_sid', models.CharField(blank=True, max_length=60, verbose_name='SID Twilio')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='Envoyé le')),
                ('conversation', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='messages',
                    to='whatsapp.whatsappconversation',
                    verbose_name='Conversation',
                )),
            ],
            options={
                'verbose_name': 'Message WhatsApp',
                'verbose_name_plural': 'Messages WhatsApp',
                'ordering': ['sent_at'],
            },
        ),
    ]
