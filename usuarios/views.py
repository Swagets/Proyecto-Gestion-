from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .forms import EditarUsuarioForm, RegistroProductoForm
from .models import Usuario


def registro_usuario(request):
    # LA IMPORTACIÓN VA AQUÍ ADENTRO:
    from .forms import RegistroUsuarioForm

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)

        if form.is_valid():
            # Recuerda: si tu usuario usa contraseña, 
            # aquí deberías usar set_password() antes del save()
            form.save()
            return redirect('registro_usuario') 

    else:
        form = RegistroUsuarioForm()

    return render(request, 'usuarios/registro_usuario.html', {'form': form})
#----------------Prodcuto-------------------
@login_required
def registrar_producto(request):
    if request.method == 'POST':
        form = RegistroProductoForm(request.POST)
        if form.is_valid():
            form.save()
            # OJO: Si aún no tienes la vista 'lista_productos', 
            # cámbiala temporalmente a 'dashboard_admin' para que no te dé error
            return redirect('dashboard_admin') 
    else:
        form = RegistroProductoForm()
        
    # Cambié la ruta a la carpeta usuarios para mantener tu estructura
    return render(request, 'usuarios/registro_producto.html', {'form': form})

@login_required
def editar_usuario(request, id):
    # Capa de seguridad: Solo el ADMIN puede editar
    if not (request.user.is_superuser or request.user.rol == 'ADMIN'):
        return redirect('redireccion_rol')

    # Buscamos al usuario por su ID
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        # Pasamos los nuevos datos y la instancia a actualizar
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin') # Volvemos al dashboard tras guardar
    else:
        # Si es GET, cargamos el formulario con los datos actuales
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario_editado': usuario})

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
    # Capa de seguridad
    if not (request.user.is_superuser or request.user.rol == 'ADMIN'):
        return redirect('redireccion_rol')
    
    # Obtenemos todos los usuarios de la base de datos
    usuarios = Usuario.objects.all()
    
    # Enviamos los usuarios a la plantilla
    return render(request, 'usuarios/dashboard_admin.html', {'usuarios': usuarios})

@login_required
def dashboard_bodega(request):
    return HttpResponse("Dashboard Bodeguero")

@login_required
def dashboard_vendedor(request):
    return HttpResponse("Dashboard Vendedor")