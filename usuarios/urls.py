from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Redirección centralizada por rol
    path('redireccion/', views.redireccion_por_rol, name='redireccion_rol'),

    # Usuarios
    path('registrar/', views.registro_usuario, name='registro_usuario'),
    path('editar/<int:id>/', views.editar_usuario, name='editar_usuario'),

    # Productos
    path('productos/registrar/', views.registrar_producto, name='registro_producto'),
    path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('productos/lista/', views.lista_productos, name='lista_productos'),

    # Proveedores
    path('proveedores/registrar/', views.registrar_proveedor, name='registrar_proveedor'),

    # Clientes
    path('clientes/registrar/', views.registrar_cliente, name='registrar_cliente'),

    # Compras
    path('compras/registrar/', views.registrar_compra, name='registrar_compra'),
    path('compras/detalle/registrar/', views.registrar_detalle_compra, name='registro_detalle_compra'),

    # Lotes
    path('compras/lotes/', views.lista_compras_lotes, name='lista_compras_lotes'),
    path('compras/<int:compra_id>/lotes/', views.lista_lotes_compra, name='lista_lotes_compra'),
    path('compras/detalle/<int:detalle_id>/lotes/registrar/', views.registrar_lote, name='registrar_lote'),
    path('compras/ubicacion/crear/', views.crear_ubicacion, name='crear_ubicacion'),

    # Inventario
    path('inventario/', views.lista_inventario, name='lista_inventario'),

    # Dashboards
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/bodega/', views.dashboard_bodega, name='dashboard_bodega'),
    path('dashboard/vendedor/', views.dashboard_vendedor, name='dashboard_vendedor'),
]
