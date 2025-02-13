from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
# Create your models here.


class usuario(models.Model):
    nombre=models.CharField(max_length=200)
    correo=models.CharField(max_length=200)
    divisa=models.CharField(max_length=3)
    balance=models.FloatField()


class categoria(models.Model):
    clave_usuario = models.ForeignKey(usuario, null=False, blank=False, on_delete=models.DO_NOTHING)
    total_transacciones = models.BigIntegerField()
    total_dinero = models.FloatField()
    tipo = models.CharField(max_length=7)
    nombre = models.CharField(max_length=200)

class subcategoria(models.Model):
    clave_categoria = models.ForeignKey(categoria, null=False, blank=False, on_delete=models.DO_NOTHING)
    total_transacciones = models.BigIntegerField()
    total_dinero = models.FloatField()
    tipo = models.CharField(max_length=7)
    nombre = models.CharField(max_length=200)

class cuenta(models.Model):
    clave_usuario = models.ForeignKey(usuario, null=False, blank=False, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=200)
    balance=models.FloatField()
    divisa=models.CharField(max_length=3)


class transaccion(models.Model):
    clave_cuenta = models.ForeignKey(cuenta, null=False, blank=False, on_delete=models.DO_NOTHING)
    clave_categoria = models.ForeignKey(categoria, null=False, blank=False, on_delete=models.DO_NOTHING)
    clave_subcategoria = models.ForeignKey(subcategoria, null=True, blank=False, on_delete=models.DO_NOTHING)
    cantidad=models.FloatField()
    tipo=models.CharField(max_length=10, default="Gasto", null=False)
    divisa=models.CharField(max_length=3)
    fecha=models.DateField()
    comentarios=models.CharField(max_length=500, null=True)
    foto = models.ImageField(upload_to='imagenes_transacciones', null=True)
    a_cuotas = models.CharField(max_length=2, default="NO")

class transferencia(models.Model):
    clave_cuenta = models.ForeignKey(cuenta, null=False, blank=False, on_delete=models.DO_NOTHING)
    tipo = models.CharField(max_length=20, null=False, default="envio")
    cantidad=models.FloatField()
    divisa=models.CharField(max_length=3)
    fecha=models.DateField()
    comentarios=models.CharField(max_length=500)


class objetivo(models.Model):
    clave_usuario = models.ForeignKey(usuario, null=False, blank=False, on_delete=models.DO_NOTHING)
    total=models.FloatField()
    asignado=models.FloatField()
    clave_categoria = models.ForeignKey(categoria, null=True, blank=False, on_delete=models.DO_NOTHING)
    fecha_limite=models.DateField()
    divisa=models.CharField(max_length=3, default="mxn")
    
class limite(models.Model):
    clave_usuario = models.ForeignKey(usuario, null=False, blank=False, on_delete=models.DO_NOTHING)
    total=models.FloatField()
    asignado=models.FloatField()
    clave_categoria = models.ForeignKey(categoria, null=True, blank=False, on_delete=models.DO_NOTHING)
    fecha_limite=models.DateField()
    divisa=models.CharField(max_length=3, default="mxn")

class cuotas(models.Model):
    clave_transaccion = models.ForeignKey(transaccion, null=False, blank=False, on_delete=models.DO_NOTHING)
    cantidad=models.FloatField()
    fecha=models.DateField()
    pendiente=models.CharField(max_length=2, default='SI')

