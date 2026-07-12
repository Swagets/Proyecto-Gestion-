from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views  # <--- ¡ESTA LÍNEA ES LA CLAVE!

urlpatterns = [
    path('login/', LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Esta es la ruta que usa tu lógica de redirección
    path('redireccion/', views.redireccion_por_rol, name='redireccion_rol'),
    path('registrar/', views.registro_usuario, name='registro_usuario'),
    path('editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('productos/registrar/', views.registrar_producto, name='registro_producto'),
    # Tus otras rutas de dashboard
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/bodega/', views.dashboard_bodega, name='dashboard_bodega'),
    path('dashboard/vendedor/', views.dashboard_vendedor, name='dashboard_vendedor'),
]