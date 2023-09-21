from django.urls import path
from .views import UsuarioView, CuentasView, CategoriasView, SubCategoriasView
urlpatterns=[
    path('usuarios/', UsuarioView.as_view(), name='usuarios_list'),
    path('usuarios/<int:id>', UsuarioView.as_view(), name='usuarios_process'),

    path('cuentas/', CuentasView.as_view(), name='cuentas_list'),
    path('cuentas/<int:id>', CuentasView.as_view(), name='cuentas_process'),

    path('categorias/', CategoriasView.as_view(), name='categorias_list'),
    path('categorias/<int:id>', CategoriasView.as_view(), name='categorias_process'),

    path('subcategorias/', SubCategoriasView.as_view(), name='subcategorias_list'),
    path('subcategorias/<int:id>', SubCategoriasView.as_view(), name='subcategorias_process')
]