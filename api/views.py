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
            datos={'message': "Cuenta no encontrada"}
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
            datos={'message': "Categoria no encontrada"}
        return JsonResponse(datos)

class SubCategoriasView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            subcategorias=list(subcategoria.objects.filter(id=id).values())
            if len(subcategorias)>0:
                aux=subcategorias[0]
                datos={'message': "Exito", "subcategoria": aux}
            else:
                datos={'message': "subcategoria no encontrada"}
            return JsonResponse(datos)
        else:
                
            subcategorias=list(subcategoria.objects.values())
            if len(subcategorias)>0:
                datos={'message': "Exito", "subcategorias": subcategorias}
            else:
                datos={'message': "subcategorias no encontradas"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        subcategoria.objects.create(clave_categoria_id=jd["clave_categoria"],total_transacciones=jd["total_transacciones"], total_dinero=jd["total_dinero"], tipo=jd["tipo"], nombre=jd["nombre"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        jd =json.loads(request.body)
        subcategorias=list(subcategoria.objects.filter(id=id).values())
        if len(subcategorias)>0:
            aux=subcategoria.objects.get(id=id)

            aux.nombre=jd["nombre"]
            aux.save()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)
    
    def delete (self,request, id):
        subcategorias=list(subcategoria.objects.filter(id=id).values())
        if len(subcategorias)>0:
            subcategoria.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Subcategoria no encontrado"}
        return JsonResponse(datos)

class TransaccionesView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            transacciones=list(transaccion.objects.filter(id=id).values())
            if len(transacciones)>0:
                aux=transacciones[0]
                datos={'message': "Exito", "transaccion": aux}
            else:
                datos={'message': "transaccion no encontrada"}
            return JsonResponse(datos)
        else:
                
            transacciones=list(transaccion.objects.values())
            if len(transacciones)>0:
                datos={'message': "Exito", "transacciones": transacciones}
            else:
                datos={'message': "transacciones no encontradas"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        transaccion.objects.create(clave_cuenta_id=jd["clave_cuenta"],
                                   clave_categoria_id=jd["clave_categoria"],
                                   clave_subcategoria_id=jd["clave_subcategoria"],
                                   cantidad=jd["cantidad"],
                                   divisa=jd["divisa"],
                                   fecha=jd["fecha"],
                                   comentarios=jd["comentarios"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        pass
    
    def delete (self,request, id):
        transacciones=list(transaccion.objects.filter(id=id).values())
        if len(transacciones)>0:
            transaccion.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Transaccion no encontrada"}
        return JsonResponse(datos)

class TransferenciasView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            transferencias=list(transferencia.objects.filter(id=id).values())
            if len(transferencias)>0:
                aux=transferencias[0]
                datos={'message': "Exito", "transferencia": aux}
            else:
                datos={'message': "transferencia no encontrada"}
            return JsonResponse(datos)
        else:
                
            transferencias=list(transferencia.objects.values())
            if len(transferencias)>0:
                datos={'message': "Exito", "transferencias": transferencias}
            else:
                datos={'message': "transferencias no encontradas"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        transferencia.objects.create(clave_cuenta_id=jd["clave_cuenta"],
                                   tipo=jd["tipo"],
                                   cantidad=jd["cantidad"],
                                   divisa=jd["divisa"],
                                   fecha=jd["fecha"],
                                   comentarios=jd["comentarios"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        pass
    
    def delete (self,request, id):
        transferencias=list(transferencia.objects.filter(id=id).values())
        if len(transferencias)>0:
            transferencia.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Transferencia no encontrado"}
        return JsonResponse(datos)




class ObjetivosView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            objetivos=list(objetivo.objects.filter(id=id).values())
            if len(objetivos)>0:
                aux=objetivos[0]
                datos={'message': "Exito", "objetivo": aux}
            else:
                datos={'message': "objetivo no encontrado"}
            return JsonResponse(datos)
        else:
                
            objetivos=list(objetivo.objects.values())
            if len(objetivos)>0:
                datos={'message': "Exito", "objetivos": objetivos}
            else:
                datos={'message': "objetivos no encontrados"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        objetivo.objects.create(clave_cuenta_id=jd["clave_cuenta"],
                                total_ingresado=jd["total_ingresado"],
                                objetivo_asignado=jd["objetivo_asignado"],
                                clave_categoria_id=jd["clave_categoria"],
                                clave_subcategoria_id=jd["clave_subcategoria"],
                                fecha_limite=jd["fecha_limite"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        pass
    
    def delete (self,request, id):
        objetivos=list(objetivo.objects.filter(id=id).values())
        if len(objetivos)>0:
            objetivo.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Objetivo no encontrado"}
        return JsonResponse(datos)


class LimitesView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            limites=list(limite.objects.filter(id=id).values())
            if len(limites)>0:
                aux=limites[0]
                datos={'message': "Exito", "limite": aux}
            else:
                datos={'message': "limite no encontrado"}
            return JsonResponse(datos)
        else:
                
            limites=list(limite.objects.values())
            if len(limites)>0:
                datos={'message': "Exito", "limites": limites}
            else:
                datos={'message': "limites no encontrados"}
            return JsonResponse(datos)

    def post (self,request):
        jd=json.loads(request.body)
        
        limite.objects.create(clave_cuenta_id=jd["clave_cuenta"],
                                total_gastado=jd["total_ingresado"],
                                limite_asignado=jd["objetivo_asignado"],
                                clave_categoria_id=jd["clave_categoria"],
                                clave_subcategoria_id=jd["clave_subcategoria"],
                                fecha_limite=jd["fecha_limite"])

        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        pass
    
    def delete (self,request, id):
        limites=list(limite.objects.filter(id=id).values())
        if len(limites)>0:
            limite.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "limite no encontrado"}
        return JsonResponse(datos)


