from django.urls import path
from .views import UsuarioView, CuentasView, CategoriasView, SubCategoriasView, TransaccionesView, TransferenciasView, ObjetivosView, LimitesView, TransaccionesRango, TransaccionesDia, TransaccionesMes, TransaccionesYear, TransaccionesSemana, CorreoRecuperacion
urlpatterns=[
    path('usuarios/', UsuarioView.as_view(), name='usuarios_list'),
    path('usuarios/<int:id>', UsuarioView.as_view(), name='usuarios_process'),

    path('cuentas/', CuentasView.as_view(), name='cuentas_list'),
    path('cuentas/<int:id>', CuentasView.as_view(), name='cuentas_process'),

    path('categorias/', CategoriasView.as_view(), name='categorias_list'),
    path('categorias/<int:id>', CategoriasView.as_view(), name='categorias_process'),

    path('subcategorias/', SubCategoriasView.as_view(), name='subcategorias_list'),
    path('subcategorias/<int:id>', SubCategoriasView.as_view(), name='subcategorias_process'),

    path('transacciones/', TransaccionesView.as_view(), name='transacciones_list'),
    path('transacciones/<int:id>', TransaccionesView.as_view(), name='transacciones_process'),

    path('transferencias/', TransferenciasView.as_view(), name='transferencias_list'),
    path('transferencias/<int:id>', TransferenciasView.as_view(), name='transferencias_process'),

    path('objetivos/', ObjetivosView.as_view(), name='objetivos_list'),
    path('objetivos/<int:id>', ObjetivosView.as_view(), name='objetivos_process'),

    path('limites/', LimitesView.as_view(), name='limites_list'),
    path('limites/<int:id>', LimitesView.as_view(), name='limites_process'),

    path('transacciones/rango/<str:tipo>/<int:categoria>/<str:fecha>/<str:fecha2>/<int:id>', TransaccionesRango.as_view(), name='transacciones_rango'),
    path('transacciones/dia/<str:tipo>/<int:categoria>/<int:id>', TransaccionesDia.as_view(), name='transacciones_dia'),
    path('transacciones/mes/<str:tipo>/<int:categoria>/<int:id>', TransaccionesMes.as_view(), name='transacciones_mes'),
    path('transacciones/year/<str:tipo>/<int:categoria>/<int:id>', TransaccionesYear.as_view(), name='transacciones_year'),
    path('transacciones/semana/<str:tipo>/<int:categoria>/<int:id>', TransaccionesSemana.as_view(), name='transacciones_semana'),

    path('correo', CorreoRecuperacion.as_view(), name="CorreoRecuperacion")
]