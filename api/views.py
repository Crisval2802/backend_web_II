from typing import Any
from django import http
from django.http.response import JsonResponse 
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import usuario, cuenta, categoria, subcategoria, transaccion, transferencia, objetivo, limite
from django.utils.decorators import method_decorator
import json


class UsuarioView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    

    def get(self,request, id=0):
        if (id>0):
            usuarios=list(usuario.objects.filter(id=id).values())
            if len(usuarios)>0:
                aux=usuarios[0]
                datos={'message': "Exito", "Usuario": aux}
            else:
                datos={'message': "Usuario no encontrado"}
            return JsonResponse(datos)
        else:
                
            usuarios=list(usuario.objects.values())
            if len(usuarios)>0:
                datos={'message': "Exito", "Usuarios": usuarios}
            else:
                datos={'message': "Usuarios no encontrados"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        usuario.objects.create(nombre=jd["nombre"], correo=jd["correo"], contra=jd["contra"], divisa=jd["divisa"], balance=jd["balance"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        jd =json.loads(request.body)
        usuarios=list(usuario.objects.filter(id=id).values())
        if len(usuarios)>0:
            aux=usuario.objects.get(id=id)

            aux.nombre=jd["nombre"]
            aux.contra=jd["contra"]
            aux.divisa=jd["divisa"]
            aux.save()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)
    
    def delete (self,request, id):
        usuarios=list(usuario.objects.filter(id=id).values())
        if len(usuarios)>0:
            usuario.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)

class CuentasView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            cuentas=list(cuenta.objects.filter(id=id).values())
            if len(cuentas)>0:
                aux=cuentas[0]
                datos={'message': "Exito", "Cuenta": aux}
            else:
                datos={'message': "Cuenta no encontrada"}
            return JsonResponse(datos)
        else:
                
            cuentas=list(cuenta.objects.values())
            if len(cuentas)>0:
                datos={'message': "Exito", "Cuentas": cuentas}
            else:
                datos={'message': "Cuentas no encontradas"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        cuenta.objects.create(clave_usuario_id=jd["clave_usuario"],nombre=jd["nombre"], balance=jd["balance"], divisa=jd["divisa"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        jd =json.loads(request.body)
        cuentas=list(cuenta.objects.filter(id=id).values())
        if len(cuentas)>0:
            aux=cuenta.objects.get(id=id)

            aux.nombre=jd["nombre"]
            aux.save()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)
    
    def delete (self,request, id):
        cuentas=list(cuenta.objects.filter(id=id).values())
        if len(cuentas)>0:
            cuenta.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)
    
class CategoriasView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            categorias=list(categoria.objects.filter(id=id).values())
            if len(categorias)>0:
                aux=categorias[0]
                datos={'message': "Exito", "Categoria": aux}
            else:
                datos={'message': "Categoria no encontrada"}
            return JsonResponse(datos)
        else:
                
            categorias=list(categoria.objects.values())
            if len(categorias)>0:
                datos={'message': "Exito", "Categorias": categorias}
            else:
                datos={'message': "Categorias no encontradas"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        categoria.objects.create(clave_usuario_id=jd["clave_usuario"],total_transacciones=jd["total_transacciones"], total_dinero=jd["total_dinero"], tipo=jd["tipo"], nombre=jd["nombre"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        jd =json.loads(request.body)
        categorias=list(categoria.objects.filter(id=id).values())
        if len(categorias)>0:
            aux=categoria.objects.get(id=id)

            aux.nombre=jd["nombre"]
            aux.save()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)
    
    def delete (self,request, id):
        categorias=list(categoria.objects.filter(id=id).values())
        if len(categorias)>0:
            categoria.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)


class SubCategoriasView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            categorias=list(categoria.objects.filter(id=id).values())
            if len(categorias)>0:
                aux=categorias[0]
                datos={'message': "Exito", "Categoria": aux}
            else:
                datos={'message': "Categoria no encontrada"}
            return JsonResponse(datos)
        else:
                
            categorias=list(categoria.objects.values())
            if len(categorias)>0:
                datos={'message': "Exito", "Categorias": categorias}
            else:
                datos={'message': "Categorias no encontradas"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        categoria.objects.create(clave_usuario_id=jd["clave_usuario"],total_transacciones=jd["total_transacciones"], total_dinero=jd["total_dinero"], tipo=jd["tipo"], nombre=jd["nombre"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        jd =json.loads(request.body)
        categorias=list(categoria.objects.filter(id=id).values())
        if len(categorias)>0:
            aux=categoria.objects.get(id=id)

            aux.nombre=jd["nombre"]
            aux.save()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)
    
    def delete (self,request, id):
        categorias=list(categoria.objects.filter(id=id).values())
        if len(categorias)>0:
            categoria.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)







