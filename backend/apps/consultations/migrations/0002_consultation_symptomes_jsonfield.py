from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultation',
            name='symptomes',
            field=models.JSONField(blank=True, default=list, verbose_name='Symptômes observés'),
        ),
    ]
