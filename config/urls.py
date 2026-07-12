# config/urls.py
from django.contrib import admin
from django.urls import path, include
from usuarios import views # Importas las vistas aquí

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    
    # La pones directamente en la ruta raíz
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/bodega/', views.dashboard_bodega, name='dashboard_bodega'),
    path('dashboard/vendedor/', views.dashboard_vendedor, name='dashboard_vendedor'),
]