import json
import datetime #para el manejo de fechas
import requests

from django.core.files.base import ContentFile
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


from django.http.response import JsonResponse 
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import usuario, cuenta, categoria, subcategoria, transaccion, transferencia, objetivo, limite, cuotas
from django.utils.decorators import method_decorator
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required


from django.conf import settings
from django.core.mail import  EmailMultiAlternatives
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
#Clases para aplicar los metodos get,post,put y delete a cada uno de los 8 modelos de la BD

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class UsuarioView(APIView):


    @method_decorator(staff_member_required(login_url='login'), name='dispatch') # Decorador para que solo las cuentas de superusuario puedan accedera esta api
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

    

    def put (self,request, id=0):
        valor_divisa=""
        jd =json.loads(request.body)
        usuarios=list(usuario.objects.filter(id=id).values())
        if len(usuarios)>0:
            aux=usuario.objects.get(id=id)
            if(jd["nombre"] !=""):
                aux.nombre=jd["nombre"]
            if(jd["contra"] !=""):
                aux.contra=jd["contra"]
                aux_user = User.objects.get(username=aux.correo)
                aux_user.set_password(jd['contra'])
                aux_user.save()
            if(jd["divisa"] !=""):
                de_divisa=aux.divisa.lower()
                a_divisa=jd["divisa"].lower()
                aux.divisa=jd["divisa"]

                url_api = "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/" + de_divisa + "/" + a_divisa + ".json"
                response = requests.get(url_api)
                if response.status_code ==200:
                    aux2 = response.json()
                    valor_divisa=aux2[a_divisa]


                    # se actualiza el balance actual del usuario
                    balance= float(aux.balance)
                    balance = balance * float(valor_divisa)

                    aux.balance=round(balance,2)

                    #se actualiza el balance de las cuentas del usuario
                    cuentas=list(cuenta.objects.filter(clave_usuario=aux.id).values())

                    if len(cuentas)>0:

                        for elemento in cuentas:
                            id_cuenta = elemento['id']
                            aux_cuenta=cuenta.objects.get(id=id_cuenta)
                            
                            balance= float(aux_cuenta.balance)
                            balance = balance * float(valor_divisa)

                            aux_cuenta.balance=round(balance,2)
                            aux_cuenta.divisa=jd["divisa"]

                            aux_cuenta.save()

                    #se actualiza el total de dinero de las categorias del usuario
                    categorias=list(categoria.objects.filter(clave_usuario=aux.id).values())

                    if len(categorias)>0:

                        for elemento in categorias:
                            id_categoria = elemento['id']
                            aux_categoria=categoria.objects.get(id=id_categoria)
                            
                            balance= float(aux_categoria.total_dinero)
                            balance = balance * float(valor_divisa)

                            aux_categoria.total_dinero=round(balance,2)

                            aux_categoria.save()

                             #se actualiza el total de dinero de las subcategorias del usuario
                            subcategorias=list(subcategoria.objects.filter(clave_categoria=aux_categoria.id).values())

                            if len(subcategorias)>0:

                                for elemento in subcategorias:
                                    id_subcategoria = elemento['id']
                                    aux_subcategoria=subcategoria.objects.get(id=id_subcategoria)
                                    
                                    balance= float(aux_subcategoria.total_dinero)
                                    balance = balance * float(valor_divisa)

                                    aux_subcategoria.total_dinero=round(balance,2)

                                    aux_subcategoria.save()
                    parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
                    #se actualiza el total de dinero de los limites y objetivos del usuario
                    limites=list(limite.objects.filter(clave_usuario=aux.id).filter(fecha_limite__gte=parsed_date).values())
                    if len(limites)>0:
                        for elemento in limites:
                            id_limite = elemento['id']
                            aux_limite=limite.objects.get(id=id_limite)
                            aux_valor= float(aux_limite.asignado)
                            aux_valor = aux_valor * float(valor_divisa)
                            aux_limite.asignado=round(aux_valor,2)
                            aux_valor= float(aux_limite.total)
                            aux_valor = aux_valor * float(valor_divisa)
                            aux_limite.total=round(aux_valor,2)
                            aux_limite.divisa=a_divisa.upper()
                            aux_limite.save()
                    #se actualiza el total de dinero de las categorias del usuario
                    objetivos=list(objetivo.objects.filter(clave_usuario=aux.id).filter(fecha_limite__gte=parsed_date).values())
                    if len(objetivos)>0:
                        for elemento in objetivos:
                            id_objetivo = elemento['id']
                            aux_objetivo=objetivo.objects.get(id=id_objetivo)
                            aux_valor= float(aux_objetivo.asignado)
                            aux_valor = aux_valor * float(valor_divisa)
                            aux_objetivo.asignado=round(aux_valor,2)
                            aux_valor= float(aux_objetivo.total)
                            aux_valor = aux_valor * float(valor_divisa)
                            aux_objetivo.total=round(aux_valor,2)
                            aux_objetivo.divisa=a_divisa.upper()
                            aux_objetivo.save()

            aux.save()
            datos={'message': "exito"}

        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)
    
    #@method_decorator(staff_member_required(login_url='login'), name='dispatch') # Decorador para que solo las cuentas de superusuario puedan accedera esta api
    def delete (self,request, id):
        usuarios=list(usuario.objects.filter(id=id).values())
        if len(usuarios)>0:
            usuario.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Usuario no encontrado"}
        return JsonResponse(datos)
    
   
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CuentasView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    @method_decorator(staff_member_required(login_url='login'), name='dispatch') # Decorador para que solo las cuentas de superusuario puedan accedera esta api
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
            datos={'message': "Cuenta no encontrada"}
        return JsonResponse(datos)
    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch') # Decorador para que solo las cuentas de superusuario puedan accedera esta api
    def delete (self,request, id):
        cuentas=list(cuenta.objects.filter(id=id).values())
        if len(cuentas)>0:
            cuenta.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Cuenta no encontrada"}
        return JsonResponse(datos)
    
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
class CategoriasView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
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
        
        categoria.objects.create(clave_usuario_id=jd["clave_usuario"],
                                 total_transacciones=0, 
                                 total_dinero=0, 
                                 tipo=jd["tipo"], 
                                 nombre=jd["nombre"])

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

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class SubCategoriasView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
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
        
        subcategoria.objects.create(clave_categoria_id=jd["clave_categoria"],
                                    total_transacciones=0, 
                                    total_dinero=0, 
                                    tipo=jd["tipo"], 
                                    nombre=jd["nombre"])

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
    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
    def delete (self,request, id):
        subcategorias=list(subcategoria.objects.filter(id=id).values())
        if len(subcategorias)>0:
            subcategoria.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Subcategoria no encontrado"}
        return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransaccionesView(APIView):

    

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
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
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")

        clave_categoria=''
        clave_subcategoria=''


        if request.POST.get('cantidad_pagos'):
            a_cuotas="SI"
        else:
            a_cuotas="NO"

        if (request.POST.get('tipo')=="Gasto"):
            transaccion.objects.create(clave_cuenta_id=request.POST.get('cuenta'),
                                    clave_categoria_id=request.POST.get('categoria_gasto'),
                                    clave_subcategoria_id=request.POST.get('subcategoria_gasto'),
                                    tipo=request.POST.get('tipo'),
                                    cantidad=request.POST.get('cantidad'),
                                    divisa=request.POST.get('divisa'),
                                    fecha=parsed_date,
                                    comentarios=request.POST.get('comentarios'),
                                    a_cuotas=a_cuotas
                                    )
            clave_categoria=request.POST.get('categoria_gasto')
            clave_subcategoria=request.POST.get('subcategoria_gasto')
        else:
            transaccion.objects.create(clave_cuenta_id=request.POST.get('cuenta'),
                                    clave_categoria_id=request.POST.get('categoria_ingreso'),
                                    clave_subcategoria_id=request.POST.get('subcategoria_ingreso'),
                                    tipo=request.POST.get('tipo'),
                                    cantidad=request.POST.get('cantidad'),
                                    divisa=request.POST.get('divisa'),
                                    fecha=parsed_date,
                                    comentarios=request.POST.get('comentarios'),
                                    a_cuotas=a_cuotas
                                    )
            clave_categoria=request.POST.get('categoria_ingreso')
            clave_subcategoria=request.POST.get('subcategoria_ingreso')


 
        imagen = request.FILES.get('imagen')
        if imagen:
            image = imagen.read()

            ultima_transaccion = transaccion.objects.latest('id')

            ultima_transaccion.foto.save('imagen_transaccion_'+ str(ultima_transaccion.id) + '.jpg',  ContentFile(image), save=False) # se guarda la nueva foto
            ultima_transaccion.save()


        if request.POST.get('cantidad_pagos'):
            ultima_transaccion = transaccion.objects.latest('id')

            cantidad_cuota= (float (request.POST.get('cantidad'))) / (float(request.POST.get('cantidad_pagos')))


            aux_fecha=parsed_date
            for i in range(int(request.POST.get('cantidad_pagos'))):
                aux= aux_fecha.split("-") # auxiliar que contendra la fecha divida en a;o, mes y dia
                cuotas.objects.create(clave_transaccion_id=ultima_transaccion.id,
                                      cantidad=cantidad_cuota,
                                      fecha=aux_fecha)
                int_aux = int(aux[1])
                
                #aumenta la fecha para la siguiente cuota
                if int_aux == 12:
                    aux[1]="1"
                    int_aux0=int(aux[0])
                    aux[0]=str(int_aux0 + 1)
                else:
                    aux[1]= str(int_aux + 1)
                aux_fecha=aux[0]+ "-" + aux[1] + "-" + aux[2]
                
        datos={'message': "Exito"}

        #Cambio de balances
        aux_cuenta=cuenta.objects.get(id=request.POST.get('cuenta'))

        clave_usuario=aux_cuenta.clave_usuario_id

        aux_usuario=usuario.objects.get(id=int(clave_usuario))


        balance=float(aux_cuenta.balance)
        # se resta o suma del balance segun sea el caso
        if (request.POST.get('tipo')=="Ingreso"):
            balance= balance + float(request.POST.get('cantidad'))
            aux_cuenta.balance=balance

            balance = float(aux_usuario.balance)
            balance = balance + float(request.POST.get('cantidad'))
            aux_usuario.balance = balance
            
            # se buscan los objetivos con fecha menor limite mayor o igual a la actual y la categoria de la transaccion
            objetivos=list(objetivo.objects.filter(clave_usuario=clave_usuario).filter(fecha_limite__gte=parsed_date).filter(clave_categoria=clave_categoria))
            if len(objetivos)>0:
                for elemento in objetivos:
                    clave= elemento.id
                    aux_objetivo=objetivo.objects.get(id=clave)
                    aux_objetivo.total = aux_objetivo.total + request.POST.get('cantidad')
                    aux_objetivo.save()
            
            # se buscan los objetivos con fecha menor limite mayor o igual a la actual y la categoria sea null
            objetivos=list(objetivo.objects.filter(clave_usuario=clave_usuario).filter(fecha_limite__gte=parsed_date).filter(clave_categoria__isnull=True))
            if len(objetivos)>0:
                for elemento in objetivos:
                    clave= elemento.id
                    aux_objetivo=objetivo.objects.get(id=clave)
                    aux_objetivo.total = aux_objetivo.total + request.POST.get('cantidad')
                    aux_objetivo.save()



        else:
            balance= balance - float(request.POST.get('cantidad'))
            aux_cuenta.balance=balance

            balance = float(aux_usuario.balance)
            balance = balance - float(request.POST.get('cantidad'))
            aux_usuario.balance = balance



            parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
            # se buscan los limites con fecha menor limite mayor o igual a la actual y la categoria de la transaccion
            limites=list(limite.objects.filter(clave_usuario=clave_usuario).filter(fecha_limite__gte=parsed_date).filter(clave_categoria=clave_categoria))
            if len(limites)>0:
                for elemento in limites:
                    clave= elemento.id
                    aux_limite=limite.objects.get(id=clave)
                    aux_limite.total = aux_limite.total + request.POST.get('cantidad')
                    aux_limite.save()
            
            # se buscan los limites con fecha menor limite mayor o igual a la actual y la categoria sea null
            limites=list(limite.objects.filter(clave_usuario=clave_usuario).filter(fecha_limite__gte=parsed_date).filter(clave_categoria__isnull=True))
            if len(limites)>0:
                for elemento in limites:
                    clave= elemento.id
                    aux_limite=limite.objects.get(id=clave)
                    aux_limite.total = aux_limite.total + request.POST.get('cantidad')
                    aux_limite.save()

        aux_cuenta.save()
        aux_usuario.save()

        #se suma al contador de transacciones de las categorias
        aux_categoria=categoria.objects.get(id=clave_categoria)
        aux_categoria.total_transacciones=aux_categoria.total_transacciones + 1
        aux_categoria.total_dinero= aux_categoria.total_dinero + float(request.POST.get('cantidad'))
        aux_categoria.save()

        if (clave_subcategoria!=''):
            aux_subcategoria=subcategoria.objects.get(id=clave_subcategoria)
            aux_subcategoria.total_transacciones=aux_subcategoria.total_transacciones + 1
            aux_subcategoria.total_dinero= aux_subcategoria.total_dinero + float(request.POST.get('cantidad'))
            aux_subcategoria.save()


        


        return JsonResponse(datos)


    def put (self,request, id=0):
        pass
    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
    def delete (self,request, id):
        transacciones=list(transaccion.objects.filter(id=id).values())
        if len(transacciones)>0:
            transaccion.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Transaccion no encontrada"}
        return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransferenciasView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
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
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        transferencia.objects.create(clave_cuenta_id=jd["clave_cuenta"],
                                   tipo="cargo",
                                   cantidad=jd["cantidad"],
                                   divisa=jd["divisa"],
                                   fecha=parsed_date,
                                   comentarios=jd["comentarios"])
        
        transferencia.objects.create(clave_cuenta_id=jd["clave_cuenta2"],
                                   tipo="abono",
                                   cantidad=jd["cantidad"],
                                   divisa=jd["divisa"],
                                   fecha=parsed_date,
                                   comentarios=jd["comentarios"])
        


        #Se resta de las cuentas y se suma segun toque:
        aux_cuenta=cuenta.objects.get(id=jd['clave_cuenta'])
        aux_cuenta.balance= aux_cuenta.balance - jd['cantidad']
        aux_cuenta.save()

        aux_cuenta=cuenta.objects.get(id=jd['clave_cuenta2'])
        aux_cuenta.balance= aux_cuenta.balance + jd['cantidad']
        aux_cuenta.save()


        datos={'message': "Exito"}
        return JsonResponse(datos)

    def put (self,request, id=0):
        pass
    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
    def delete (self,request, id):
        transferencias=list(transferencia.objects.filter(id=id).values())
        if len(transferencias)>0:
            transferencia.objects.filter(id=id).delete()
            datos={'message': "Exito"}
        else:
            datos={'message': "Transferencia no encontrado"}
        return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ObjetivosView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
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
        
        if jd["categoria"]=="Any":
            objetivo.objects.create(clave_usuario_id=jd["clave_usuario"],
                                total=0,
                                asignado=jd["asignado"],
                                fecha_limite=jd["fecha_limite"],
                                divisa=jd["divisa"])
        else:
            objetivo.objects.create(clave_usuario_id=jd["clave_usuario"],
                                total=0,
                                asignado=jd["asignado"],
                                clave_categoria_id=jd["categoria"],
                                fecha_limite=jd["fecha_limite"],
                                divisa=jd["divisa"])

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

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class LimitesView(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(staff_member_required(login_url='login'), name='dispatch')
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
        
        if jd["categoria"]=="Any":
            limite.objects.create(clave_usuario_id=jd["clave_usuario"],
                                total=0,
                                asignado=jd["asignado"],
                                fecha_limite=jd["fecha_limite"],
                                divisa=jd["divisa"])
        else:
            limite.objects.create(clave_usuario_id=jd["clave_usuario"],
                                total=0,
                                asignado=jd["asignado"],
                                clave_categoria_id=jd["categoria"],
                                fecha_limite=jd["fecha_limite"],
                                divisa=jd["divisa"])

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



#Clase que contiene el metodo get para obtener las transacciones realizadas entre dos fechas y un usuario especifico
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransaccionesRango(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self,request, tipo="",clave_categoria=0, fecha="",fecha2="", id=0):
        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=int(clave_categoria)).order_by("fecha").values())

                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).order_by("fecha").values())
                    
                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).order_by("fecha").values())
                    else:
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).order_by("fecha").values())#__range sirve para obtener registros entre 2 rangos de fechas
                    

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_final=[]
                    #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                    for elemento in lista_transacciones:
                        #para obtener las cuentas
                        aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                        for aux_cuenta in aux_cuentas:
                            elemento['nombre_cuenta']=aux_cuenta['nombre']
                        #para obtener las categorias
                        aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                        for aux_categoria in aux_categorias:
                            elemento['nombre_categoria']=aux_categoria['nombre']
                        #para obtener las subcategorias
                        aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                        if len(aux_subcategorias)>0:
                            for aux_subcategoria in aux_subcategorias:
                                elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                        else:
                            elemento['nombre_subcategoria']="**Ninguna**"

                        lista_final.append(elemento)


                    datos={'message': "Exito", "Transacciones": lista_final}
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)

#Clase que contiene el metodo get para obtener las transacciones realizadas un dia especifico


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransaccionesDia(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    def get(self,request, tipo="",clave_categoria=0, id=0):
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")

        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=clave_categoria).values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).values())

                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).values())
                        
                    else:
                        
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).values())
                        

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_final=[]
                    #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                    for elemento in lista_transacciones:
                        #para obtener las cuentas
                        aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                        for aux_cuenta in aux_cuentas:
                            elemento['nombre_cuenta']=aux_cuenta['nombre']
                        #para obtener las categorias
                        aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                        for aux_categoria in aux_categorias:
                            elemento['nombre_categoria']=aux_categoria['nombre']
                        #para obtener las subcategorias
                        aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                        if len(aux_subcategorias)>0:
                            for aux_subcategoria in aux_subcategorias:
                                elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                        else:
                            elemento['nombre_subcategoria']="**Ninguna**"

                        lista_final.append(elemento)


                    datos = {'message': 'Exito', "Transacciones": lista_final}
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)
                    

        
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransaccionesMes(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

    def get(self,request,tipo="",clave_categoria=0, id=0):
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        aux= parsed_date.split("-")
        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=clave_categoria).order_by("fecha").values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).order_by("fecha").values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).order_by("fecha").values())
                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).order_by("fecha").values())

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_filtrada=[]

                    for elemento in lista_transacciones:
                        fecha=(elemento['fecha'].strftime("%Y-%m-%d")).split("-")
                        if fecha[1]==aux[1] and fecha[0]==aux[0]:
                            lista_filtrada.append(elemento)

                    if len(lista_filtrada)>0:
                        lista_final=[]
                        #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                        for elemento in lista_filtrada:
                            #para obtener las cuentas
                            aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                            for aux_cuenta in aux_cuentas:
                                elemento['nombre_cuenta']=aux_cuenta['nombre']
                            #para obtener las categorias
                            aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                            for aux_categoria in aux_categorias:
                                elemento['nombre_categoria']=aux_categoria['nombre']
                            #para obtener las subcategorias
                            aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                            if len(aux_subcategorias)>0:
                                for aux_subcategoria in aux_subcategorias:
                                    elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                            else:
                                elemento['nombre_subcategoria']="**Ninguna**"

                            lista_final.append(elemento)


                        datos={'message': "Exito", "Transacciones": lista_final}
                        return JsonResponse(datos)
                    else:
                        datos={'message': "No se encontraron transacciones asociados a ese usuario"}
                        return JsonResponse(datos)
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
                    return JsonResponse(datos)
                    
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)
                    

#Clase que contiene el metodo get para obtener las transacciones realizadas un Mes especifico
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransaccionesYear(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request,tipo="",clave_categoria=0, id=0):
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        aux= parsed_date.split("-")
            
        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=clave_categoria).order_by("fecha").values())

                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).order_by("fecha").values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).order_by("fecha").values())
                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).order_by("fecha").values())
                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_filtrada=[]

                    for elemento in lista_transacciones:
                        fecha=(elemento['fecha'].strftime("%Y-%m-%d")).split("-")
                        if fecha[0]==aux[0]:
                            lista_filtrada.append(elemento)


                    if len(lista_filtrada)>0:
                        lista_final=[]
                        #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                        for elemento in lista_filtrada:
                            #para obtener las cuentas
                            aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                            for aux_cuenta in aux_cuentas:
                                elemento['nombre_cuenta']=aux_cuenta['nombre']
                            #para obtener las categorias
                            aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                            for aux_categoria in aux_categorias:
                                elemento['nombre_categoria']=aux_categoria['nombre']
                            #para obtener las subcategorias
                            aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                            if len(aux_subcategorias)>0:
                                for aux_subcategoria in aux_subcategorias:
                                    elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                            else:
                                elemento['nombre_subcategoria']="**Ninguna**"

                            lista_final.append(elemento)


                        datos={'message': "Exito", "Transacciones": lista_final}
                        return JsonResponse(datos)
                    else:
                        datos={'message': "No se encontraron transacciones asociados a ese usuario"}
                        return JsonResponse(datos)
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
                    return JsonResponse(datos)
                    
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)
  
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)
                    


                

#Clase que contiene el metodo get para obtener las transacciones realizadas la semnaa actual
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransaccionesSemana(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self,request,tipo="",clave_categoria=0, id=0):
        aux2=date.today()

        #print(aux2.weekday())

        fecha_inicial=["0000","00","00"]
        fecha_final=["0000","00","00"]

        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d") # Se obtiene la fecha actual en formato YYYY-MM-DD

        aux= parsed_date.split("-") # auxiliar que contendra la fecha divida en a;o, mes y dia

        if (aux2.weekday()==0): # Es lunes
            if (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12"): # se validan meses con 31 dias
                if ((int(aux[2]) + 6) > 31): # se da un brinco de mes entre el inicio y el fin de semana
                    dias_restantes= "0" + str((int(aux[2]) + 6) - 31)
                    if (aux[1]=="12"): #Es diciembre y se tiene que guardar los datos de la fecha final del rango de la semana
                        fecha_final[0] = str(int(aux[0])+1) #Se suma 1 al a;o
                        fecha_final[1] = "01"   # El mes es enero
                        fecha_final[2] = dias_restantes

                        fecha_inicial[0] = aux[0]
                        fecha_inicial[1] = aux[1]
                        fecha_inicial[2] = aux[2]

                        print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                        print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
                    else:
                        fecha_final[0] = aux[0]
                        
                        if (int(aux[1]) + 1>9): # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                            fecha_final[1] =str (int(aux[1]) + 1)
                        else:
                            fecha_final[1] ="0" + str(int(aux[1]) + 1)
                        fecha_final[2] = dias_restantes
                        
                        
                        fecha_inicial[0] = aux[0]
                        fecha_inicial[1] = aux[1]
                        fecha_inicial[2] = aux[2]

                        print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                        print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
                
                else:
                    fecha_final[0] = aux[0]
                    fecha_final[1] = aux[1]
                    if ((int(aux[2]) + 6) > 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_final[2] =str (int(aux[2]) + 6)
                    else:
                        fecha_final[2] ="0" + str(int(aux[2]) + 6)


                    fecha_inicial[0] = aux[0]
                    fecha_inicial[1] = aux[1]
                    fecha_inicial[2] = aux[2]

                    print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                    print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])


            elif (aux[1]=="02"):
                if ((int(aux[2]) + 6) > 28):
                    dias_restantes= "0" + str((int(aux[2]) + 6) - 28)
                    
                    fecha_final[0] = aux[0]
                    
                    fecha_final[1] = "03"
                    
                    fecha_final[2] = dias_restantes

                    fecha_inicial[0] = aux[0]
                    fecha_inicial[1] = aux[1]
                    fecha_inicial[2] = aux[2]

                    print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                    print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

                else:
                    fecha_final[0] = aux[0]
                    fecha_final[1] = aux[1]

                    if ((int(aux[2]) + 6) > 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_final[2] =str (int(aux[2]) + 6)
                    else:
                        fecha_final[2] ="0" + str(int(aux[2]) + 6)


                    fecha_inicial[0] = aux[0]
                    fecha_inicial[1] = aux[1]
                    fecha_inicial[2] = aux[2]

                    print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                    print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # se validan meses con 30 dias
                if ((int(aux[2]) + 6) > 30):
                    dias_restantes= "0" + str((int(aux[2]) + 6) - 30)
                    if (aux[1]=="12"): #Es diciembre y se tiene que guardar los datos de la fecha final del rango de la semana
                        fecha_final[0] = str(int(aux[0])+1) #Se suma 1 al a;o
                        fecha_final[1] = "01"   # El mes es enero
                        fecha_final[2] = dias_restantes

                        fecha_inicial[0] = aux[0]
                        fecha_inicial[1] = aux[1]
                        fecha_inicial[2] = aux[2]

                        print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                        print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
                    else:
                        fecha_final[0] = aux[0]
                        
                        if (int(aux[1]) + 1>9): # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                            fecha_final[1] =str (int(aux[1]) + 1)
                        else:
                            fecha_final[1] ="0" + str(int(aux[1]) + 1)
                        fecha_final[2] = dias_restantes
                        
                        
                        fecha_inicial[0] = aux[0]
                        fecha_inicial[1] = aux[1]
                        fecha_inicial[2] = aux[2]

                        print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                        print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
                else:
                    fecha_final[0] = aux[0]
                    fecha_final[1] = aux[1]
                    if ((int(aux[2]) + 6) > 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_final[2] =str (int(aux[2]) + 6)
                    else:
                        fecha_final[2] ="0" + str(int(aux[2]) + 6)

                    fecha_inicial[0] = aux[0]
                    fecha_inicial[1] = aux[1]
                    fecha_inicial[2] = aux[2]

                    print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                    print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==1): # Es martes
            if (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+5)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            elif ((int(aux[2]) + 5> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 5) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-1)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            elif ((int(aux[2]) + 5> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 5) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-1)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            elif ((int(aux[2]) + 5> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 5) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-1)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-1)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-1)
                else:
                    fecha_inicial[2]=str(int(aux[2])-1)

                if((int(aux[2])+5)<10):
                    fecha_final[2]="0" + str(int(aux[2])+5)
                else:
                    fecha_final[2]=str(int(aux[2])+5)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==2): # Es miercoles
            if (aux[2]=="02"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+4)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "30"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "30"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "27"
                    else:
                        fecha_inicial[2] = "29"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+4)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 4> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 4) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-2)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 4> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 4) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-2)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 4> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 4) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-2)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-2)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-2)
                else:
                    fecha_inicial[2]=str(int(aux[2])-2)

                if((int(aux[2])+4)<10):
                    fecha_final[2]="0" + str(int(aux[2])+4)
                else:
                    fecha_final[2]=str(int(aux[2])+4)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==3): # Es jueves
            if (aux[2]=="03"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+3)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="02"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "30"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "30"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "27"
                    else:
                        fecha_inicial[2] = "29"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+3)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "29"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "29"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "26"
                    else:
                        fecha_inicial[2] = "28"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+3)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 3> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 3) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-3)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 3> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 3) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-3)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 3> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 3) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-3)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-3)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-3)
                else:
                    fecha_inicial[2]=str(int(aux[2])-3)

                if((int(aux[2])+3)<10):
                    fecha_final[2]="0" + str(int(aux[2])+3)
                else:
                    fecha_final[2]=str(int(aux[2])+3)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==4): # Es viernes
            if (aux[2]=="04"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+2)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="03"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "30"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "30"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "27"
                    else:
                        fecha_inicial[2] = "29"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+2)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="02"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "29"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "29"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "26"
                    else:
                        fecha_inicial[2] = "28"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+2)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "28"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "28"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "25"
                    else:
                        fecha_inicial[2] = "27"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+2)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 2> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 2) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-4)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 2> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 2) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-4)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 2> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 2) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-4)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-4)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-4)
                else:
                    fecha_inicial[2]=str(int(aux[2])-4)

                if((int(aux[2])+2)<10):
                    fecha_final[2]="0" + str(int(aux[2])+2)
                else:
                    fecha_final[2]=str(int(aux[2])+2)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==5): # Es sabado
            if (aux[2]=="05"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="04"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "30"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "30"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "27"
                    else:
                        fecha_inicial[2] = "29"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="03"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "29"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "29"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "26"
                    else:
                        fecha_inicial[2] = "28"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="02"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "28"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "28"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "25"
                    else:
                        fecha_inicial[2] = "27"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            elif (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "27"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "27"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "24"
                    else:
                        fecha_inicial[2] = "26"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 1> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 1) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-5)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 1> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 1) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-5)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 1> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 1) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-5)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-5)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-5)
                else:
                    fecha_inicial[2]=str(int(aux[2])-5)

                if((int(aux[2])+1)<10):
                    fecha_final[2]="0" + str(int(aux[2])+1)
                else:
                    fecha_final[2]=str(int(aux[2])+1)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==6): # es domingo

            if ((int(aux[2]) - 6) < 1): # se da un brinco de mes entre el inicio y el fin de semana
                dias_restantes=(6 - int(aux[2]))
                if (aux[1]=="01"):
                    mes_anterior="12"
                    fecha_inicial[0]=str(int(aux[0])-1)
                else:
                    if((int(aux[1])-1)<10):    # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        mes_anterior="0" + str(int(aux[1])-1)
                    else:
                        mes_anterior=str(int(aux[1])-1)
                    fecha_inicial[0]=aux[0]
                fecha_inicial[1]=mes_anterior
                if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10" or mes_anterior=="12"):
                    fecha_inicial[2]=str(31-dias_restantes)
                elif (mes_anterior=="02"):
                    fecha_inicial[2]=str(28-dias_restantes)
                else:
                    fecha_inicial[2]=str(30-dias_restantes)
                fecha_final[0] = aux[0]
                fecha_final[1] = aux[1]
                fecha_final[2] = aux[2]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

                
            else: # solo se resta para llegar al rango de fechas
                fecha_inicial[0] = aux[0]
                fecha_inicial[1] = aux[1]
                if ((int(aux[2]) - 6) > 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                    fecha_inicial[2] =str (int(aux[2]) - 6)
                else:
                    fecha_inicial[2] ="0" + str(int(aux[2]) - 6)


                fecha_final[0] = aux[0]
                fecha_final[1] = aux[1]
                fecha_final[2] = aux[2]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            

        inicio=fecha_inicial[0]+"-" + fecha_inicial[1]+"-"+fecha_inicial[2]
        final=fecha_final[0]+"-" + fecha_final[1]+"-"+fecha_final[2]

        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=clave_categoria).filter(fecha__range=(inicio, final)).order_by("fecha").values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).filter(fecha__range=(inicio, final)).order_by("fecha").values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(fecha__range=(inicio, final)).order_by("fecha").values())
                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(fecha__range=(inicio, final)).order_by("fecha").values())
                    
                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_final=[]
                    #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                    for elemento in lista_transacciones:
                        #para obtener las cuentas
                        aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                        for aux_cuenta in aux_cuentas:
                            elemento['nombre_cuenta']=aux_cuenta['nombre']
                        #para obtener las categorias
                        aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                        for aux_categoria in aux_categorias:
                            elemento['nombre_categoria']=aux_categoria['nombre']
                        #para obtener las subcategorias
                        aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                        if len(aux_subcategorias)>0:
                            for aux_subcategoria in aux_subcategorias:
                                elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                        else:
                            elemento['nombre_subcategoria']="**Ninguna**"

                        lista_final.append(elemento)


                    datos={'message': "Exito", "Inicio": inicio, "Final": final,"Transacciones": lista_final}
                    
                else:
                    datos={'message': "No se encontraron cuentas", "Inicio": inicio, "Final": final}
            else:
                datos={'message': "No se encontraron cuentas", "Inicio": inicio, "Final": final}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)
        
        

class CorreoRecuperacion(APIView):  
      
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self,request):
        jd=json.loads(request.body)
        user = User.objects.get(email=jd["correo"])
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"http://127.0.0.1:8000/api/reset/{uid}/{token}/"
            
            subject = 'Recuperación de contraseña'
            message = f'Para restablecer su contraseña, haga clic en el siguiente enlace: {reset_url}'
            from_email = settings.EMAIL_HOST_USER
            to_email = jd['correo']
            
            msg=EmailMultiAlternatives(subject, message, from_email, [to_email])
            msg.send()
            datos={'message': "Correo enviado exitosamente"}
            return JsonResponse(datos)
        else:
            datos={'message': "No se encontro un usuario con ese correo"}
            return JsonResponse(datos)
        
    
        
#Clases para generar reportes

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ReporteRango(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self,request, tipo="",clave_categoria=0, fecha="",fecha2="", id=0):
        if (id>0):

            # Se obtiene el nombre del usuario
            usuarios=list(usuario.objects.filter(id=id).values())

            for aux in usuarios:
                nombre_usuario=aux['nombre']

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=int(clave_categoria)).values())

                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).values())
                    
                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).values())
                    else:
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).values())#__range sirve para obtener registros entre 2 rangos de fechas
                    

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_final=[]
                    #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                    for elemento in lista_transacciones:
                        #para obtener las cuentas
                        aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                        for aux_cuenta in aux_cuentas:
                            elemento['nombre_cuenta']=aux_cuenta['nombre']
                        #para obtener las categorias
                        aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                        for aux_categoria in aux_categorias:
                            elemento['nombre_categoria']=aux_categoria['nombre']
                        #para obtener las subcategorias
                        aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                        if len(aux_subcategorias)>0:
                            for aux_subcategoria in aux_subcategorias:
                                elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                        else:
                            elemento['nombre_subcategoria']="**Ninguna**"

                        lista_final.append(elemento)


                    datos={'message': "Exito", "Transacciones": lista_final,"fecha": date.today(), "usuario":nombre_usuario}
                    #Proceso para convertir el html a pdf
                    template = get_template('reporte.html')
                    html = template.render({"datos":datos}) # Aqui se pasa el json con los datos obtenidos
                    
                    # Crear un objeto HttpResponse con el tipo de contenido adecuado para PDF
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="Reporte de transacciones.pdf"'

                    # Convierte el HTML a PDF y escribe en la respuesta
                    pisa_status = pisa.CreatePDF(html, dest=response)
                    
                    # Si la conversión tuvo éxito, devuelve la respuesta
                    if pisa_status.err:
                        return HttpResponse('Error al generar el PDF')
                    
                    return response
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
class ReporteDia(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self,request, tipo="",clave_categoria=0, fecha="",fecha2="", id=0):
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")

        if (id>0):
            # Se obtiene el nombre del usuario
            usuarios=list(usuario.objects.filter(id=id).values())

            for aux in usuarios:
                nombre_usuario=aux['nombre']

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=clave_categoria).values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).values())

                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).values())
                        
                    else:
                        
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).values())
                        

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_final=[]
                    #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                    for elemento in lista_transacciones:
                        #para obtener las cuentas
                        aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                        for aux_cuenta in aux_cuentas:
                            elemento['nombre_cuenta']=aux_cuenta['nombre']
                        #para obtener las categorias
                        aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                        for aux_categoria in aux_categorias:
                            elemento['nombre_categoria']=aux_categoria['nombre']
                        #para obtener las subcategorias
                        aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                        if len(aux_subcategorias)>0:
                            for aux_subcategoria in aux_subcategorias:
                                elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                        else:
                            elemento['nombre_subcategoria']="**Ninguna**"

                        lista_final.append(elemento)


                    datos={'message': "Exito", "Transacciones": lista_final, "fecha": date.today(), "usuario":nombre_usuario}
                    #Proceso para convertir el html a pdf
                    template = get_template('reporte.html')
                    html = template.render({"datos":datos}) # Aqui se pasa el json con los datos obtenidos
                    
                    # Crear un objeto HttpResponse con el tipo de contenido adecuado para PDF
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="Reporte de transacciones.pdf"'

                    # Convierte el HTML a PDF y escribe en la respuesta
                    pisa_status = pisa.CreatePDF(html, dest=response)
                    
                    # Si la conversión tuvo éxito, devuelve la respuesta
                    if pisa_status.err:
                        return HttpResponse('Error al generar el PDF')
                    
                    return response
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
class ReporteMes(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self,request,tipo="",clave_categoria=0, id=0):
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        aux= parsed_date.split("-")
        if (id>0):
            
            # Se obtiene el nombre del usuario
            usuarios=list(usuario.objects.filter(id=id).values())

            for aux_user in usuarios:
                nombre_usuario=aux_user['nombre']

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=clave_categoria).values())
                        
                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).values())
                        
                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).values())

                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).values())

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_filtrada=[]

                    for elemento in lista_transacciones:
                        fecha=(elemento['fecha'].strftime("%Y-%m-%d")).split("-")
                        if fecha[1]==aux[1] and fecha[0]==aux[0]:
                            lista_filtrada.append(elemento)

                    if len(lista_filtrada)>0:
                        lista_final=[]
                        #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                        for elemento in lista_filtrada:
                            #para obtener las cuentas
                            aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                            for aux_cuenta in aux_cuentas:
                                elemento['nombre_cuenta']=aux_cuenta['nombre']
                            #para obtener las categorias
                            aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                            for aux_categoria in aux_categorias:
                                elemento['nombre_categoria']=aux_categoria['nombre']
                            #para obtener las subcategorias
                            aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                            if len(aux_subcategorias)>0:
                                for aux_subcategoria in aux_subcategorias:
                                    elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                            else:
                                elemento['nombre_subcategoria']="**Ninguna**"

                            lista_final.append(elemento)


                        datos={'message': "Exito", "Transacciones": lista_final, "fecha": date.today(), "usuario":nombre_usuario}
                        #Proceso para convertir el html a pdf
                        template = get_template('reporte.html')
                        html = template.render({"datos":datos}) # Aqui se pasa el json con los datos obtenidos
                        
                        # Crear un objeto HttpResponse con el tipo de contenido adecuado para PDF
                        response = HttpResponse(content_type='application/pdf')
                        response['Content-Disposition'] = 'attachment; filename="Reporte de transacciones.pdf"'

                        # Convierte el HTML a PDF y escribe en la respuesta
                        pisa_status = pisa.CreatePDF(html, dest=response)
                        
                        # Si la conversión tuvo éxito, devuelve la respuesta
                        if pisa_status.err:
                            return HttpResponse('Error al generar el PDF')
                        
                        return response
                    else:
                        datos={'message': "No se encontraron transacciones asociadooos a ese usuario"}
                        return JsonResponse(datos)
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
                    return JsonResponse(datos)
                    
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])                    
class ReporteYear(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self,request,tipo="",clave_categoria=0, id=0):
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        aux= parsed_date.split("-")
            
        if (id>0):
            
             # Se obtiene el nombre del usuario
            usuarios=list(usuario.objects.filter(id=id).values())

            for aux_user in usuarios:
                nombre_usuario=aux_user['nombre']

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=clave_categoria).values())

                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).values())
                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).values())
                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_filtrada=[]

                    for elemento in lista_transacciones:
                        fecha=(elemento['fecha'].strftime("%Y-%m-%d")).split("-")
                        if fecha[0]==aux[0]:
                            lista_filtrada.append(elemento)


                    if len(lista_filtrada)>0:
                        lista_final=[]
                        #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                        for elemento in lista_filtrada:
                            #para obtener las cuentas
                            aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                            for aux_cuenta in aux_cuentas:
                                elemento['nombre_cuenta']=aux_cuenta['nombre']
                            #para obtener las categorias
                            aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                            for aux_categoria in aux_categorias:
                                elemento['nombre_categoria']=aux_categoria['nombre']
                            #para obtener las subcategorias
                            aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                            if len(aux_subcategorias)>0:
                                for aux_subcategoria in aux_subcategorias:
                                    elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                            else:
                                elemento['nombre_subcategoria']="**Ninguna**"

                            lista_final.append(elemento)


                        datos={'message': "Exito", "Transacciones": lista_final, "fecha": date.today(), "usuario":nombre_usuario}
                        #Proceso para convertir el html a pdf
                        template = get_template('reporte.html')
                        html = template.render({"datos":datos}) # Aqui se pasa el json con los datos obtenidos
                        
                        # Crear un objeto HttpResponse con el tipo de contenido adecuado para PDF
                        response = HttpResponse(content_type='application/pdf')
                        response['Content-Disposition'] = 'attachment; filename="Reporte de transacciones.pdf"'

                        # Convierte el HTML a PDF y escribe en la respuesta
                        pisa_status = pisa.CreatePDF(html, dest=response)
                        
                        # Si la conversión tuvo éxito, devuelve la respuesta
                        if pisa_status.err:
                            return HttpResponse('Error al generar el PDF')
                        
                        return response
                    else:
                        datos={'message': "No se encontraron transacciones asociados a ese usuario"}
                        return JsonResponse(datos)
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
                    return JsonResponse(datos)
                    
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)
  
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ReporteSemana(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self,request,tipo="",clave_categoria=0, id=0):
        aux2=date.today()

        #print(aux2.weekday())

        fecha_inicial=["0000","00","00"]
        fecha_final=["0000","00","00"]

        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d") # Se obtiene la fecha actual en formato YYYY-MM-DD

        aux= parsed_date.split("-") # auxiliar que contendra la fecha divida en a;o, mes y dia

        if (aux2.weekday()==0): # Es lunes
            if (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12"): # se validan meses con 31 dias
                if ((int(aux[2]) + 6) > 31): # se da un brinco de mes entre el inicio y el fin de semana
                    dias_restantes= "0" + str((int(aux[2]) + 6) - 31)
                    if (aux[1]=="12"): #Es diciembre y se tiene que guardar los datos de la fecha final del rango de la semana
                        fecha_final[0] = str(int(aux[0])+1) #Se suma 1 al a;o
                        fecha_final[1] = "01"   # El mes es enero
                        fecha_final[2] = dias_restantes

                        fecha_inicial[0] = aux[0]
                        fecha_inicial[1] = aux[1]
                        fecha_inicial[2] = aux[2]

                        print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                        print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
                    else:
                        fecha_final[0] = aux[0]
                        
                        if (int(aux[1]) + 1>9): # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                            fecha_final[1] =str (int(aux[1]) + 1)
                        else:
                            fecha_final[1] ="0" + str(int(aux[1]) + 1)
                        fecha_final[2] = dias_restantes
                        
                        
                        fecha_inicial[0] = aux[0]
                        fecha_inicial[1] = aux[1]
                        fecha_inicial[2] = aux[2]

                        print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                        print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
                
                else:
                    fecha_final[0] = aux[0]
                    fecha_final[1] = aux[1]
                    if ((int(aux[2]) + 6) > 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_final[2] =str (int(aux[2]) + 6)
                    else:
                        fecha_final[2] ="0" + str(int(aux[2]) + 6)


                    fecha_inicial[0] = aux[0]
                    fecha_inicial[1] = aux[1]
                    fecha_inicial[2] = aux[2]

                    print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                    print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])


            elif (aux[1]=="02"):
                if ((int(aux[2]) + 6) > 28):
                    dias_restantes= "0" + str((int(aux[2]) + 6) - 28)
                    
                    fecha_final[0] = aux[0]
                    
                    fecha_final[1] = "03"
                    
                    fecha_final[2] = dias_restantes

                    fecha_inicial[0] = aux[0]
                    fecha_inicial[1] = aux[1]
                    fecha_inicial[2] = aux[2]

                    print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                    print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

                else:
                    fecha_final[0] = aux[0]
                    fecha_final[1] = aux[1]

                    if ((int(aux[2]) + 6) > 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_final[2] =str (int(aux[2]) + 6)
                    else:
                        fecha_final[2] ="0" + str(int(aux[2]) + 6)


                    fecha_inicial[0] = aux[0]
                    fecha_inicial[1] = aux[1]
                    fecha_inicial[2] = aux[2]

                    print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                    print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # se validan meses con 30 dias
                if ((int(aux[2]) + 6) > 30):
                    dias_restantes= "0" + str((int(aux[2]) + 6) - 30)
                    if (aux[1]=="12"): #Es diciembre y se tiene que guardar los datos de la fecha final del rango de la semana
                        fecha_final[0] = str(int(aux[0])+1) #Se suma 1 al a;o
                        fecha_final[1] = "01"   # El mes es enero
                        fecha_final[2] = dias_restantes

                        fecha_inicial[0] = aux[0]
                        fecha_inicial[1] = aux[1]
                        fecha_inicial[2] = aux[2]

                        print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                        print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
                    else:
                        fecha_final[0] = aux[0]
                        
                        if (int(aux[1]) + 1>9): # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                            fecha_final[1] =str (int(aux[1]) + 1)
                        else:
                            fecha_final[1] ="0" + str(int(aux[1]) + 1)
                        fecha_final[2] = dias_restantes
                        
                        
                        fecha_inicial[0] = aux[0]
                        fecha_inicial[1] = aux[1]
                        fecha_inicial[2] = aux[2]

                        print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                        print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
                else:
                    fecha_final[0] = aux[0]
                    fecha_final[1] = aux[1]
                    if ((int(aux[2]) + 6) > 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_final[2] =str (int(aux[2]) + 6)
                    else:
                        fecha_final[2] ="0" + str(int(aux[2]) + 6)

                    fecha_inicial[0] = aux[0]
                    fecha_inicial[1] = aux[1]
                    fecha_inicial[2] = aux[2]

                    print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                    print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==1): # Es martes
            if (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+5)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            elif ((int(aux[2]) + 5> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 5) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-1)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            elif ((int(aux[2]) + 5> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 5) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-1)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            elif ((int(aux[2]) + 5> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 5) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-1)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-1)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-1)
                else:
                    fecha_inicial[2]=str(int(aux[2])-1)

                if((int(aux[2])+5)<10):
                    fecha_final[2]="0" + str(int(aux[2])+5)
                else:
                    fecha_final[2]=str(int(aux[2])+5)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==2): # Es miercoles
            if (aux[2]=="02"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+4)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "30"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "30"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "27"
                    else:
                        fecha_inicial[2] = "29"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+4)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 4> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 4) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-2)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 4> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 4) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-2)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 4> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 4) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-2)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-2)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-2)
                else:
                    fecha_inicial[2]=str(int(aux[2])-2)

                if((int(aux[2])+4)<10):
                    fecha_final[2]="0" + str(int(aux[2])+4)
                else:
                    fecha_final[2]=str(int(aux[2])+4)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==3): # Es jueves
            if (aux[2]=="03"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+3)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="02"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "30"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "30"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "27"
                    else:
                        fecha_inicial[2] = "29"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+3)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "29"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "29"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "26"
                    else:
                        fecha_inicial[2] = "28"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+3)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 3> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 3) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-3)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 3> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 3) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-3)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 3> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 3) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-3)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-3)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-3)
                else:
                    fecha_inicial[2]=str(int(aux[2])-3)

                if((int(aux[2])+3)<10):
                    fecha_final[2]="0" + str(int(aux[2])+3)
                else:
                    fecha_final[2]=str(int(aux[2])+3)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==4): # Es viernes
            if (aux[2]=="04"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+2)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="03"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "30"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "30"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "27"
                    else:
                        fecha_inicial[2] = "29"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+2)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="02"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "29"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "29"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "26"
                    else:
                        fecha_inicial[2] = "28"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+2)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "28"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "28"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "25"
                    else:
                        fecha_inicial[2] = "27"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+2)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 2> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 2) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-4)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 2> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 2) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-4)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 2> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 2) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-4)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-4)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-4)
                else:
                    fecha_inicial[2]=str(int(aux[2])-4)

                if((int(aux[2])+2)<10):
                    fecha_final[2]="0" + str(int(aux[2])+2)
                else:
                    fecha_final[2]=str(int(aux[2])+2)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==5): # Es sabado
            if (aux[2]=="05"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "31"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "31"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "28"
                    else:
                        fecha_inicial[2] = "30"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="04"): #Es el segundo del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "30"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "30"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "27"
                    else:
                        fecha_inicial[2] = "29"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="03"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "29"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "29"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "26"
                    else:
                        fecha_inicial[2] = "28"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif (aux[2]=="02"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "28"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "28"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "25"
                    else:
                        fecha_inicial[2] = "27"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            elif (aux[2]=="01"): #Es el primero del mes y por ende el dia anterior corresponde al mes anterior
                if (aux[1]=="01"):
                    fecha_inicial[0] = str(int(aux[0])-1)
                    fecha_inicial[1] = "12"
                    fecha_inicial[2] = "27"
                else:
                    fecha_inicial[0] = aux[0]
                    if (int(aux[1])-1 >= 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        fecha_inicial[1] =str (int(aux[1])-1)
                        mes_anterior=str(int(aux[1])-1)
                    else:
                        fecha_inicial[1] ="0" + str(int(aux[1])-1)
                        mes_anterior="0" + str(int(aux[1])-1)

                    if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10"):
                        fecha_inicial[2] = "27"
                    elif (mes_anterior=="02"):
                        fecha_inicial[2] = "24"
                    else:
                        fecha_inicial[2] = "26"

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]
                fecha_final[2]="0" + str (int(aux[2])+1)


                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 1> 31) and (aux[1]=="01" or aux[1]=="03" or aux[1]=="05" or aux[1]=="07" or aux[1]=="08" or aux[1]=="10" or aux[1]=="12")): #la semana finaliza en el mes siguiente
                if (aux[1]=="12"): # se cambia de anio
                    fecha_final[0]= str(int(aux[0]) + 1)
                    fecha_final[1]= "01"
                else:
                    fecha_final[0]=aux[0] #el anio queda igual
                    if((int(aux[1])+1)<10):
                        fecha_final[1]="0" + str(int(aux[1])+1)
                    else:
                        fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 1) - 31)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-5)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 1> 28) and aux[1]=="02"):
                fecha_final[0]=aux[0]
                fecha_final[1]="03"
                
                dias_restantes= "0" + str((int(aux[2]) + 1) - 28)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-5)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            elif ((int(aux[2]) + 1> 30) and (aux[1]=="04" or aux[1]=="06" or aux[1]=="09" or aux[1]=="11")):

                fecha_final[0]=aux[0] #el anio queda igual
                if((int(aux[1])+1)<10):
                    fecha_final[1]="0" + str(int(aux[1])+1)
                else:
                    fecha_final[1]=str(int(aux[1])+1)
                

                dias_restantes= "0" + str((int(aux[2]) + 1) - 30)
                fecha_final[2] = dias_restantes

                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]
                fecha_inicial[2]= str(int(aux[2])-5)

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])
            else: # la semana inicia y termina el mismo mes
                fecha_inicial[0]=aux[0]
                fecha_inicial[1]=aux[1]

                if((int(aux[2])-5)<10):
                    fecha_inicial[2]="0" + str(int(aux[2])-5)
                else:
                    fecha_inicial[2]=str(int(aux[2])-5)

                if((int(aux[2])+1)<10):
                    fecha_final[2]="0" + str(int(aux[2])+1)
                else:
                    fecha_final[2]=str(int(aux[2])+1)

                fecha_final[0]=aux[0]
                fecha_final[1]=aux[1]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

        elif (aux2.weekday()==6): # es domingo

            if ((int(aux[2]) - 6) < 1): # se da un brinco de mes entre el inicio y el fin de semana
                dias_restantes=(6 - int(aux[2]))
                if (aux[1]=="01"):
                    mes_anterior="12"
                    fecha_inicial[0]=str(int(aux[0])-1)
                else:
                    if((int(aux[1])-1)<10):    # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                        mes_anterior="0" + str(int(aux[1])-1)
                    else:
                        mes_anterior=str(int(aux[1])-1)
                    fecha_inicial[0]=aux[0]
                fecha_inicial[1]=mes_anterior
                if (mes_anterior=="01" or mes_anterior=="03" or mes_anterior=="05" or mes_anterior=="07" or mes_anterior=="08" or mes_anterior=="10" or mes_anterior=="12"):
                    fecha_inicial[2]=str(31-dias_restantes)
                elif (mes_anterior=="02"):
                    fecha_inicial[2]=str(28-dias_restantes)
                else:
                    fecha_inicial[2]=str(30-dias_restantes)
                fecha_final[0] = aux[0]
                fecha_final[1] = aux[1]
                fecha_final[2] = aux[2]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

                
            else: # solo se resta para llegar al rango de fechas
                fecha_inicial[0] = aux[0]
                fecha_inicial[1] = aux[1]
                if ((int(aux[2]) - 6) > 10) : # Validacion para evitar conflictos con el formato, ya que si es menor a 10 es resultado puede quedar por ejemplo como 9 en vez de 09
                    fecha_inicial[2] =str (int(aux[2]) - 6)
                else:
                    fecha_inicial[2] ="0" + str(int(aux[2]) - 6)


                fecha_final[0] = aux[0]
                fecha_final[1] = aux[1]
                fecha_final[2] = aux[2]

                print(fecha_inicial[0]  + " " + fecha_inicial[1] + " " + fecha_inicial[2])
                print(fecha_final[0]  + " " + fecha_final[1] + " " + fecha_final[2])

            

        inicio=fecha_inicial[0]+"-" + fecha_inicial[1]+"-"+fecha_inicial[2]
        final=fecha_final[0]+"-" + fecha_final[1]+"-"+fecha_final[2]

        if (id>0):
            
            # Se obtiene el nombre del usuario
            usuarios=list(usuario.objects.filter(id=id).values())

            for aux_user in usuarios:
                nombre_usuario=aux_user['nombre']

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=clave_categoria).filter(fecha__range=(inicio, final)).values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and clave_categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(clave_categoria=clave_categoria).filter(fecha__range=(inicio, final)).values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and clave_categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(fecha__range=(inicio, final)).values())
                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(fecha__range=(inicio, final)).values())
                    
                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_final=[]
                    #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                    for elemento in lista_transacciones:
                        #para obtener las cuentas
                        aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                        for aux_cuenta in aux_cuentas:
                            elemento['nombre_cuenta']=aux_cuenta['nombre']
                        #para obtener las categorias
                        aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                        for aux_categoria in aux_categorias:
                            elemento['nombre_categoria']=aux_categoria['nombre']
                        #para obtener las subcategorias
                        aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                        if len(aux_subcategorias)>0:
                            for aux_subcategoria in aux_subcategorias:
                                elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                        else:
                            elemento['nombre_subcategoria']="**Ninguna**"

                        lista_final.append(elemento)


                    datos={'message': "Exito", "Transacciones": lista_final, "fecha": date.today(), "usuario":nombre_usuario}
                    #Proceso para convertir el html a pdf
                    template = get_template('reporte.html')
                    html = template.render({"datos":datos}) # Aqui se pasa el json con los datos obtenidos
                    
                    # Crear un objeto HttpResponse con el tipo de contenido adecuado para PDF
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="Reporte de transacciones.pdf"'

                    # Convierte el HTML a PDF y escribe en la respuesta
                    pisa_status = pisa.CreatePDF(html, dest=response)
                    
                    # Si la conversión tuvo éxito, devuelve la respuesta
                    if pisa_status.err:
                        return HttpResponse('Error al generar el PDF')
                    
                    return response
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)


#Clases para obtener los limites y objtivos de determinado usuario
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class LimitesUsuario(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, id=0):
        if (id>0):
            limites=list(limite.objects.filter(clave_usuario=id).values().order_by("-fecha_limite"))
            if len(limites)>0:
                lista_final=[]
                #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                for elemento in limites:


                    aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                    if len(aux_categorias)>0:
                        for aux_subcategoria in aux_categorias:
                            elemento['nombre_categoria']=aux_subcategoria['nombre']
                    else:
                        elemento['nombre_categoria']="**Ninguna**"

                    lista_final.append(elemento)



                datos={'message': "Exito", "datos": lista_final}
            else:
                datos={'message': "limites no encontrados"}


        else:   
            datos={'message': "Ingrese un id para poder buscar"}
           
        return JsonResponse(datos)
        
#Clases para obtener los limites y objtivos de determinado usuario
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ObjetivosUsuario(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    def get(self,request, id=0):
        if (id>0):
            objetivos=list(objetivo.objects.filter(clave_usuario=id).values().order_by("-fecha_limite"))
            if len(objetivos)>0:
                lista_final=[]
                #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                for elemento in objetivos:


                    aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                    if len(aux_categorias)>0:
                        for aux_subcategoria in aux_categorias:
                            elemento['nombre_categoria']=aux_subcategoria['nombre']
                    else:
                        elemento['nombre_categoria']="**Ninguna**"

                    lista_final.append(elemento)




                datos={'message': "Exito", "datos": lista_final}
            else:
                datos={'message': "limites no encontrados"}


        else:   
            datos={'message': "Ingrese un id para poder buscar"}
           
        return JsonResponse(datos)

#Clases para obtener las cuentas de un usuario especifico
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CuentasUsuario(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(login_required, name='dispatch')
    def get(self,request, id=0):
        if (id>0):
            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())
            if len(cuentas)>0:
                datos={'message': "Exito", "cuentas": cuentas}
            else:
                datos={'message': "cuentas no encontradas"}


        else:   
            datos={'message': "Ingrese un id para poder buscar"}
           
        return JsonResponse(datos)
    
#Clases para obtener las categorias de un determinado usuario
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CategoriasUsuario(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(login_required, name='dispatch')
    def get(self,request, id=0):
        if (id>0):
            categorias=list(categoria.objects.filter(clave_usuario=id).values())
            if len(categorias)>0:
                


                datos={'message': "Exito", "Categorias": categorias}
            else:
                datos={'message': "Categorias no encontradas"}


        else:   
            datos={'message': "Ingrese un id para poder buscar"}
           
        return JsonResponse(datos)
    
#Clases para obtener las subcategorias de un determinado usuario
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class SubCategoriasUsuario(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(login_required, name='dispatch')
    def get(self,request, id=0):
        if (id>0):
            categorias=list(categoria.objects.filter(clave_usuario=id).values())
            if len(categorias)>0:
                lista_sub=[]

                for elemento in categorias:


                    subcategorias=list(subcategoria.objects.filter(clave_categoria=elemento["id"]).values())
                    

                    if len(subcategorias)>0:
                        for elemento2 in subcategorias:
                            lista_sub.append(elemento2)


                if len(lista_sub)>0:

                    datos={'message': "Exito", "Subcategorias": lista_sub}
                else:
                    datos={'message': "Subcategorias no encontradas"}
            else:
                datos={'message': "Categorias no encontradas"}


        else:   
            datos={'message': "Ingrese un id para poder buscar"}
           
        return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransferenciasUsuario(APIView): #Se requiere login

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    #Metodo para que sea necesario estar logeado @method_decorator(login_required, name='dispatch')
    @method_decorator(login_required, name='dispatch')
    def get(self,request, id=0):
        if (id>0):


            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transferencias=[]   
                for elemento in cuentas:
                    transferencias=list(transferencia.objects.filter(clave_cuenta=elemento["id"]).values())
                        

                    if len(transferencias)>0:
                        for elemento2 in transferencias:
                            lista_transferencias.append(elemento2)

                if len(lista_transferencias)>0:
                    lista_final=[]
                    #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                    for elemento in lista_transferencias:
                        #para obtener las cuentas
                        aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                        for aux_cuenta in aux_cuentas:
                            elemento['nombre_cuenta']=aux_cuenta['nombre']
                        lista_final.append(elemento)
                    datos={'message': "Exito", "transferencias": lista_final}
                else:
                    datos={'message': "No se encontraron transferencias"}
                return JsonResponse(datos)
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                return JsonResponse(datos)
        else:

            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)

class Login(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        jd=json.loads(request.body)
        # username = request.POST.get('correo')
        # password = request.POST.get('contra')
        username = jd['correo']
        password = jd['contra']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            aux_usuario = usuario.objects.get(correo=jd['correo'])
            token, created = Token.objects.get_or_create(user=user)
            datos={'message': "Inicio correcto", "token": token.key, "correo": username, "nombre":aux_usuario.nombre, "divisa": aux_usuario.divisa, "id": aux_usuario.id}
            return JsonResponse(datos)
        else:
            datos={'message': "Inicio Incorrecto"}
            return JsonResponse(datos)
    
class Crear_Usuario(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
    def post (self,request):
        jd=json.loads(request.body)
        

        usuarios=list(usuario.objects.filter(correo=jd["correo"]).values())
        if len(usuarios)>0:
            datos={'message': "Error, ya existe un registro con ese correo"}
            return JsonResponse(datos)
        else:
            #se crea el usuario
            usuario.objects.create(nombre=jd["nombre"], correo=jd["correo"], divisa=jd["divisa"], balance=jd["balance"])
            #Se crea el usuario para el login
            user = User.objects.create_user(jd["correo"], jd["correo"], jd["contra"])
            user.save()

            #se crea la cuenta
            aux_usuario=usuario.objects.get(correo=jd['correo'])
            cuenta.objects.create(clave_usuario_id=aux_usuario.id,nombre=jd["cuenta"], balance=jd["balance"], divisa=jd["divisa"])
            
            datos={'message': "Exito"}
            return JsonResponse(datos)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class Obtener_Balance(APIView):
     def get(self,request, id=0):
        
        if (id>0):
        
            aux_usuario= usuario.objects.get(id=id)

            datos={'message': "Exito", "balance": aux_usuario.balance}
                    
            return JsonResponse(datos)
            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)
                    
#Clases para obtener las categorias de un determinado usuario
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CategoriasGastoUsuario(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(login_required, name='dispatch')
    def get(self,request, id=0, tipo=''):
        if (id>0):
            categorias=list(categoria.objects.filter(clave_usuario=id).filter(tipo='Gasto').values())
            if len(categorias)>0:
                


                datos={'message': "Exito", "Categorias": categorias}
            else:
                datos={'message': "Categorias no encontradas"}


        else:   
            datos={'message': "Ingrese un id para poder buscar"}
           
        return JsonResponse(datos)
    

#Clases para obtener las categorias de un determinado usuario
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CategoriasIngresoUsuario(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @method_decorator(login_required, name='dispatch')
    def get(self,request, id=0, tipo=''):
        if (id>0):
            categorias=list(categoria.objects.filter(clave_usuario=id).filter(tipo='Ingreso').values())
            if len(categorias)>0:
                


                datos={'message': "Exito", "Categorias": categorias}
            else:
                datos={'message': "Categorias no encontradas"}


        else:   
            datos={'message': "Ingrese un id para poder buscar"}
           
        return JsonResponse(datos)
    

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class Obtener_Informacion_Usuario(APIView):
     def get(self,request, id=0):
        
        if (id>0):
        
            aux_usuario= usuario.objects.get(id=id)

            datos={'message': "Exito", 
                   "balance": aux_usuario.balance, 
                   "nombre": aux_usuario.nombre,
                   "correo": aux_usuario.correo,
                   "divisa": aux_usuario.divisa}
                    
            return JsonResponse(datos)
            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class TransferenciasCuenta(APIView): #Se requiere login

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def get(self,request, id=0):
        if (id>0):

            transferencias=list(transferencia.objects.filter(clave_cuenta=id).values())
                        

            if len(transferencias)>0:
                   
                datos={'message': "Exito", "Transferencias": transferencias}
            else:
                datos={'message': "No se encontraron transferencias"}
            return JsonResponse(datos)
        
        else:
            datos={'message': "Ingrese un Id para poder buscar"}
            return JsonResponse(datos)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PagosCuotas(APIView):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    def get(self,request, tipo="",clave_categoria=0, id=0):
        

        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(a_cuotas="SI").values())
                        

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    lista_final=[]
                    #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
                    for elemento in lista_transacciones:
                        #para obtener las cuentas
                        aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                        for aux_cuenta in aux_cuentas:
                            elemento['nombre_cuenta']=aux_cuenta['nombre']
                        #para obtener las categorias
                        aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                        for aux_categoria in aux_categorias:
                            elemento['nombre_categoria']=aux_categoria['nombre']
                        #para obtener las subcategorias
                        aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                        if len(aux_subcategorias)>0:
                            for aux_subcategoria in aux_subcategorias:
                                elemento['nombre_subcategoria']=aux_subcategoria['nombre']
                        else:
                            elemento['nombre_subcategoria']="**Ninguna**"

                        lista_final.append(elemento)

                    lista_cuotas=[]
                    for elemento in lista_final:
                        aux_cuotas=list(cuotas.objects.filter(clave_transaccion=elemento["id"]).values())
                        if len(aux_cuotas)>0:
                            for elemento2 in aux_cuotas:
                                lista_cuotas.append(elemento2)


                    datos = {'message': 'Exito', "Transacciones": lista_final, "Cuotas": lista_cuotas}
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)
 
