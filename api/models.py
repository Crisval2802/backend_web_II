from django.db import models

# Create your models here.


class usuario(models.Model):
    nombre=models.CharField(max_length=200)
    correo=models.CharField(max_length=200)
    contra=models.CharField(max_length=200)
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
    divisa=models.CharField(max_length=3)
    fecha=models.DateField()
    comentarios=models.CharField(max_length=500)

class transferencia(models.Model):
    clave_cuenta = models.ForeignKey(cuenta, null=False, blank=False, on_delete=models.DO_NOTHING)
    tipo = models.CharField(max_length=20, null=False, default="envio")
    cantidad=models.FloatField()
    divisa=models.CharField(max_length=3)
    fecha=models.DateField()
    comentarios=models.CharField(max_length=500)


class objetivo(models.Model):
    clave_cuenta = models.ForeignKey(cuenta, null=False, blank=False, on_delete=models.DO_NOTHING)
    total_ingresado=models.FloatField()
    objetivo_asignado=models.FloatField()
    clave_categoria = models.ForeignKey(categoria, null=False, blank=False, on_delete=models.DO_NOTHING)
    clave_subcategoria = models.ForeignKey(subcategoria, null=True, blank=False, on_delete=models.DO_NOTHING)
    fecha_limite=models.DateField()

class limite(models.Model):
    clave_cuenta = models.ForeignKey(cuenta, null=False, blank=False, on_delete=models.DO_NOTHING)
    total_gastado=models.FloatField()
    limite_asignado=models.FloatField()
    clave_categoria = models.ForeignKey(categoria, null=False, blank=False, on_delete=models.DO_NOTHING)
    clave_subcategoria = models.ForeignKey(subcategoria, null=True, blank=False, on_delete=models.DO_NOTHING)
    fecha_limite=models.DateField()


