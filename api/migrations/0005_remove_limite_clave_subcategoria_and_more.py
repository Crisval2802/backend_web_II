# Generated by Django 4.2.6 on 2023-10-08 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_transaccion_tipo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='limite',
            name='clave_subcategoria',
        ),
        migrations.RemoveField(
            model_name='objetivo',
            name='clave_subcategoria',
        ),
    ]
