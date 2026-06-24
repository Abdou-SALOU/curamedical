from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='statut_validation',
            field=models.CharField(
                choices=[
                    ('EN_ATTENTE', 'En attente de validation'),
                    ('VALIDE', 'Validé'),
                    ('REFUSE', 'Refusé'),
                ],
                default='VALIDE',
                max_length=12,
                verbose_name='Statut de validation',
            ),
        ),
    ]
