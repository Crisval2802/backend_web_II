import json
import datetime #para el manejo de fechas
import requests


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


from typing import Any
from django import http
from django.http.response import JsonResponse 
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import usuario, cuenta, categoria, subcategoria, transaccion, transferencia, objetivo, limite
from django.utils.decorators import method_decorator
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives

#Clases para aplicar los metodos get,post,put y delete a cada uno de los 8 modelos de la BD
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
        valor_divisa=""
        jd =json.loads(request.body)
        usuarios=list(usuario.objects.filter(id=id).values())
        if len(usuarios)>0:
            aux=usuario.objects.get(id=id)

            if(jd["nombre"] !=""):
                aux.nombre=jd["nombre"]
            
            if(jd["contra"] !=""):
                aux.contra=jd["contra"]
            
            if(jd["divisa"] !=""):
                de_divisa=aux.divisa
                a_divisa=jd["divisa"]
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
             
                        
                                      

            
            
            
            
            aux.save()
            datos={'message': "Exito", "Valor": valor_divisa}
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
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        transaccion.objects.create(clave_cuenta_id=jd["clave_cuenta"],
                                   clave_categoria_id=jd["clave_categoria"],
                                   clave_subcategoria_id=jd["clave_subcategoria"],
                                   tipo=jd["tipo"],
                                   cantidad=jd["cantidad"],
                                   divisa=jd["divisa"],
                                   fecha=parsed_date,
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
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        transferencia.objects.create(clave_cuenta_id=jd["clave_cuenta"],
                                   tipo="cargo",
                                   cantidad=jd["cantidad"],
                                   divisa=jd["divisa"],
                                   fecha=parsed_date,
                                   comentarios=jd["comentarios"])
        
        transferencia.objects.create(clave_cuenta_id=jd["clave_cuenta_2"],
                                   tipo="abono",
                                   cantidad=jd["cantidad"],
                                   divisa=jd["divisa"],
                                   fecha=parsed_date,
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

#Clase que contiene el metodo get para obtener las transacciones realizadas entre dos fechas y un usuario especifico
class TransaccionesRango(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request, tipo="",categoria=0, fecha="",fecha2="", id=0):
        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if ((tipo=="Ingreso" or tipo=="Gasto") and categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=int(categoria)).values())

                    elif((tipo!="Ingreso" and tipo!="Gasto") and categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(clave_categoria=categoria).values())
                    
                    elif((tipo=="Ingreso" or tipo=="Gasto") and categoria==0):
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).values())
                    else:
                        transacciones=list(transaccion.objects.filter(fecha__range=(fecha, fecha2)).filter(clave_cuenta=elemento["id"]).values())#__range sirve para obtener registros entre 2 rangos de fechas
                    

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    datos={'message': "Exito", "Transacciones": lista_transacciones}
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)

#Clase que contiene el metodo get para obtener las transacciones realizadas un dia especifico
class TransaccionesDia(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    

    def get(self,request, tipo="",categoria=0, id=0):
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")

        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if (tipo=="Ingreso" or tipo=="Gasto" and categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=categoria).values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and categoria!=0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(clave_categoria=categoria).values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and categoria==0):
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).values())
                    else:
                        transacciones=list(transaccion.objects.filter(fecha=parsed_date).filter(clave_cuenta=elemento["id"]).values())

                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    datos={'message': "Exito", "Transacciones": lista_transacciones}
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)
                    

        
#Clase que contiene el metodo get para obtener las transacciones realizadas un Mes especifico
class TransaccionesMes(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request,tipo="",categoria=0, id=0):
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        aux= parsed_date.split("-")
        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if (tipo=="Ingreso" or tipo=="Gasto" and categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=id).filter(tipo=tipo).filter(clave_categoria=categoria).values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=id).filter(clave_categoria=categoria).values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=id).filter(tipo=tipo).values())
                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=id).values())

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
                        datos={'message': "Exito", "Transaccion": lista_filtrada}
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
class TransaccionesYear(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request,tipo="",categoria=0, id=0):
        
        parsed_date = datetime.strftime(date.today(), "%Y-%m-%d")
        aux= parsed_date.split("-")
            
        if (id>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id).values())


            if len(cuentas)>0:
                lista_transacciones=[]   
                for elemento in cuentas:
                    if (tipo=="Ingreso" or tipo=="Gasto" and categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=id).filter(tipo=tipo).filter(clave_categoria=categoria).values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=id).filter(clave_categoria=categoria).values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=id).filter(tipo=tipo).values())
                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=id).values())
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
                        datos={'message': "Exito", "Transaccion": lista_filtrada}
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
class TransaccionesSemana(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request,tipo="",categoria=0, id=0):
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
                    if (tipo=="Ingreso" or tipo=="Gasto" and categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(clave_categoria=categoria).filter(fecha__range=(inicio, final)).values())
                    elif((tipo!="Ingreso" and tipo!="Gasto") and categoria!=0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(clave_categoria=categoria).filter(fecha__range=(inicio, final)).values())
                    elif((tipo=="Ingreso" or tipo=="Gasto") and categoria==0):
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(tipo=tipo).filter(fecha__range=(inicio, final)).values())
                    else:
                        transacciones=list(transaccion.objects.filter(clave_cuenta=elemento["id"]).filter(fecha__range=(inicio, final)).values())
                    
                    if len(transacciones)>0:
                        for elemento2 in transacciones:
                            lista_transacciones.append(elemento2)

                if len(lista_transacciones)>0:
                    datos={'message': "Exito","Inicio": inicio, "Final": final, "Transacciones": lista_transacciones}
                    
                else:
                    datos={'message': "No se encontraron transacciones asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)


            
        else:
            datos={'message': "Ingrese un id para poder buscar"}
            return JsonResponse(datos)
        
        
        
        


class CorreoRecuperacion(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self,request):
        jd=json.loads(request.body)
        correos=list(usuario.objects.filter(correo=jd["txt_email"]).values())
        if len(correos)>0:
            for correo in correos:

                asunto = "Mensaje de Django"
                mensaje = "Esto es un mensaje de prueba para el envio de correos:\nTu contraseña es: " + correo['contra']
                email_desde = settings.EMAIL_HOST_USER
                email_para = jd["txt_email"]
                msg=EmailMultiAlternatives(asunto, mensaje, email_desde, [email_para])
                msg.send()


                datos={'message': "correo enviado"}
                return JsonResponse(datos)
        else:
            datos={'message': "correo no encontrado"}
            return JsonResponse(datos)
        

class LimitesUsuario(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    def get(self,request, id_usuario=0):
        if (id_usuario>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id_usuario).values())

            if len(cuentas)>0:
                lista_limites=[]   
                for elemento in cuentas:
                    limites=list(limite.objects.filter(clave_cuenta=elemento["id"]).values())

                    if len(limites)>0:
                        for elemento2 in limites:
                            lista_limites.append(elemento2)

                if len(lista_limites)>0:
                    datos={'message': "Exito", "limites": lista_limites}
                    
                else:
                    datos={'message': "No se encontraron limites asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)

        else:
                

            datos={'message': "Ingrese un codigo de usuario para buscar"}
            return JsonResponse(datos)
        


class ObjetivosUsuario(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    def get(self,request, id_usuario=0):
        if (id_usuario>0):
            

            cuentas=list(cuenta.objects.filter(clave_usuario=id_usuario).values())

            if len(cuentas)>0:
                lista_objetivos=[]   
                for elemento in cuentas:
                    objetivos=list(objetivo.objects.filter(clave_cuenta=elemento["id"]).values())

                    if len(objetivos)>0:
                        for elemento2 in objetivos:
                            lista_objetivos.append(elemento2)

                if len(lista_objetivos)>0:
                    datos={'message': "Exito", "limites": lista_objetivos}
                    
                else:
                    datos={'message': "No se encontraron objetivos asociados a ese usuario"}
            else:
                datos={'message': "No se encontraron cuentas asociadas a ese usuario"}
                    
            return JsonResponse(datos)

        else:
                

            datos={'message': "Ingrese un codigo de usuario para buscar"}
            return JsonResponse(datos)
        


class ObtenerDivisa(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request, de_divisa="", a_divisa=""):
        url_api = "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/" + de_divisa + "/" + a_divisa + ".json"
        response = requests.get(url_api)
        if response.status_code ==200:
            aux = response.json()
            #valor_divisa=[a_divisa]
            datos = {'message':"Exito", "divisa": aux}
        else:
            
            datos={'message': "Error al consumir la API"}

        return JsonResponse(datos)
    

class FormatoReporte(View):    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request, id=""):

        transacciones=list(transaccion.objects.values())




        if len(transacciones)>0:
            lista_final=[]
            #Proceso para obtener el los nombres y no se muestre el numero de las llaves foraneas
            for elemento in transacciones:
                #para obtener las cuentas
                aux_cuentas= cuenta.objects.filter(id=elemento['clave_cuenta_id']).values()
                for aux_cuenta in aux_cuentas:
                    elemento['clave_cuenta_id']=aux_cuenta['nombre']
                #para obtener las categorias
                aux_categorias= categoria.objects.filter(id=elemento['clave_categoria_id']).values()
                for aux_categoria in aux_categorias:
                    elemento['clave_categoria_id']=aux_categoria['nombre']
                #para obtener las subcategorias
                aux_subcategorias= subcategoria.objects.filter(id=elemento['clave_subcategoria_id']).values()
                if len(aux_subcategorias)>0:
                    for aux_subcategoria in aux_subcategorias:
                        elemento['clave_subcategoria_id']=aux_subcategoria['nombre']
                else:
                    elemento['clave_subcategoria_id']="**Ninguna**"

                lista_final.append(elemento)

            datos={"transacciones": lista_final,"fecha": date.today(), "usuario":"Cristian Armando Valenzuela Acosta"}
        else:
            datos={'message': "transacciones no encontradas"}


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
    
        



        