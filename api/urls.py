from django.urls import path
from .views import CategoriasGastoUsuario, CategoriasIngresoUsuario, CategoriasUsuario, Crear_Transaccion, Crear_Usuario, CuentasUsuario, Login,  Obtener_Balance, Obtener_Informacion_Usuario, ReporteMes, ReporteSemana, ReporteYear, SubCategoriasUsuario, TransferenciasCuenta, TransferenciasUsuario, UsuarioView, CuentasView, CategoriasView, SubCategoriasView, TransaccionesView, TransferenciasView, ObjetivosView, LimitesView, TransaccionesRango, TransaccionesDia, TransaccionesMes, TransaccionesYear, TransaccionesSemana, CorreoRecuperacion, LimitesUsuario, ObjetivosUsuario, ObtenerDivisa, FormatoReporte, ReporteRango, ReporteDia
urlpatterns=[
    path('usuarios/', UsuarioView.as_view(), name='usuarios_list'),
    path('usuarios/<int:id>', UsuarioView.as_view(), name='usuarios_process'),

    path('cuentas/', CuentasView.as_view(), name='cuentas_list'),
    path('cuentas/<int:id>', CuentasView.as_view(), name='cuentas_process'),
    path('cuentas/usuario/<int:id>', CuentasUsuario.as_view(), name='cuentas_usuario_process'),

    path('categorias/', CategoriasView.as_view(), name='categorias_list'),
    path('categorias/<int:id>', CategoriasView.as_view(), name='categorias_process'),
    path('categorias/usuario/<int:id>', CategoriasUsuario.as_view(), name='categorias_usuario'),
    path('categorias/usuario/gasto/<int:id>', CategoriasGastoUsuario.as_view(), name='categorias_usuario_gasto'),
    path('categorias/usuario/ingreso/<int:id>', CategoriasIngresoUsuario.as_view(), name='categorias_ingreso_gasto'),

    path('subcategorias/', SubCategoriasView.as_view(), name='subcategorias_list'),
    path('subcategorias/<int:id>', SubCategoriasView.as_view(), name='subcategorias_process'),
    path('subcategorias/usuario/<int:id>', SubCategoriasUsuario.as_view(), name='subcategorias_usuario'),

    path('transacciones/', TransaccionesView.as_view(), name='transacciones_list'),
    path('transacciones/<int:id>', TransaccionesView.as_view(), name='transacciones_process'),

    path('transferencias/', TransferenciasView.as_view(), name='transferencias_list'),
    path('transferencias/<int:id>', TransferenciasView.as_view(), name='transferencias_process'),
    path('transferencias/usuario/<int:id>', TransferenciasUsuario.as_view(), name='transferencias_usuario'),
    path('transferencias/cuenta/<int:id>', TransferenciasCuenta.as_view(), name='transferencias_cuenta'),

    path('objetivos/', ObjetivosView.as_view(), name='objetivos_list'),
    path('objetivos/<int:id>', ObjetivosView.as_view(), name='objetivos_process'),
    path('objetivos/usuario/<int:id>', ObjetivosUsuario.as_view(), name='objetivos_usuario'),

    path('limites/', LimitesView.as_view(), name='limites_list'),
    path('limites/<int:id>', LimitesView.as_view(), name='limites_process'),
    path('limites/usuario/<int:id>', LimitesUsuario.as_view(), name='limites_usuario'),

    path('transacciones/rango/<str:tipo>/<int:clave_categoria>/<str:fecha>/<str:fecha2>/<int:id>', TransaccionesRango.as_view(), name='transacciones_rango'),
    path('transacciones/dia/<str:tipo>/<int:clave_categoria>/<int:id>', TransaccionesDia.as_view(), name='transacciones_dia'),
    path('transacciones/mes/<str:tipo>/<int:clave_categoria>/<int:id>', TransaccionesMes.as_view(), name='transacciones_mes'),
    path('transacciones/year/<str:tipo>/<int:clave_categoria>/<int:id>', TransaccionesYear.as_view(), name='transacciones_year'),
    path('transacciones/semana/<str:tipo>/<int:clave_categoria>/<int:id>', TransaccionesSemana.as_view(), name='transacciones_semana'),

    path('correo', CorreoRecuperacion.as_view(), name="CorreoRecuperacion"),
    path('obtenerdivisa/<str:de_divisa>/<str:a_divisa>', ObtenerDivisa.as_view(), name="ObtenerDivisa"),


    path('reporte', FormatoReporte.as_view(), name="FormatoReporte"),
    path('reporte/rango/<str:tipo>/<int:clave_categoria>/<str:fecha>/<str:fecha2>/<int:id>', ReporteRango.as_view(), name='reporte_rango'),
    path('reporte/dia/<str:tipo>/<int:clave_categoria>/<int:id>', ReporteDia.as_view(), name='reporte_dia'),
    path('reporte/mes/<str:tipo>/<int:clave_categoria>/<int:id>', ReporteMes.as_view(), name='reporte_mes'),
    path('reporte/year/<str:tipo>/<int:clave_categoria>/<int:id>', ReporteYear.as_view(), name='reporte_year'),
    path('reporte/semana/<str:tipo>/<int:clave_categoria>/<int:id>', ReporteSemana.as_view(), name='reporte_semana'),




    path('login', Login.as_view(), name='login'),



    path('crear/usuarios/', Crear_Usuario.as_view(), name='usuarios_create'),
    path('crear/transaccion/', Crear_Transaccion.as_view(), name='transaccion_create'),

    path('obtener/balance/<int:id>', Obtener_Balance.as_view(), name='Obtener_balance'),
    path('obtener/informacion/usuario/<int:id>', Obtener_Informacion_Usuario.as_view(), name='Obtener_Informacion_Usuario'),
]