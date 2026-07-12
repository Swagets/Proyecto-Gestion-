from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect

@login_required
def redireccion_por_rol(request):
    """
    Esta es la función que te faltaba y la que causa el error.
    """
    if request.user.is_superuser or request.user.rol == 'ADMIN':
        return redirect('dashboard_admin')
    elif request.user.rol == 'BODEGA':
        return redirect('dashboard_bodega')
    elif request.user.rol == 'VENDEDOR':
        return redirect('dashboard_vendedor')
    else:
        return HttpResponse("Rol no reconocido")

@login_required
def dashboard_admin(request):
    return HttpResponse("Dashboard Administrador")

@login_required
def dashboard_bodega(request):
    return HttpResponse("Dashboard Bodeguero")

@login_required
def dashboard_vendedor(request):
    return HttpResponse("Dashboard Vendedor")