# Generated by Django 4.2.4 on 2023-12-07 05:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_transaccion_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaccion',
            name='a_cuotas',
            field=models.CharField(default='NO', max_length=2),
        ),
        migrations.CreateModel(
            name='cuotas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.FloatField()),
                ('fecha', models.DateField()),
                ('clave_transaccion', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.transaccion')),
            ],
        ),
    ]
