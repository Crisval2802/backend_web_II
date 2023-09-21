from django.contrib import admin
from .models import usuario, categoria, cuenta, subcategoria, transaccion, transferencia, objetivo, limite
# Register your models here.
admin.site.register(usuario)
admin.site.register(categoria)
admin.site.register(subcategoria)
admin.site.register(cuenta)
admin.site.register(transaccion)
admin.site.register(transferencia)
admin.site.register(objetivo)
admin.site.register(limite)