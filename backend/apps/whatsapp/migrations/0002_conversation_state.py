from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='whatsappconversation',
            name='state',
            field=models.CharField(default='idle', max_length=50, verbose_name='État'),
        ),
        migrations.AddField(
            model_name='whatsappconversation',
            name='state_data',
            field=models.JSONField(blank=True, default=dict, verbose_name="Données d'état"),
        ),
    ]
