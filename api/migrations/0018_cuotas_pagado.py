# Generated by Django 4.2.4 on 2023-12-07 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_transaccion_a_cuotas_cuotas'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuotas',
            name='pagado',
            field=models.CharField(default='NO', max_length=2),
        ),
    ]
