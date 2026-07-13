from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .forms import EditarUsuarioForm, RegistroProductoForm, EditarProductoForm, ProveedorForm, ClienteForm, CompraForm, RegistroDetalleCompraForm   
from .models import Usuario, Producto, Proveedor, Cliente, Compra
from django.db.models import Q # Importante para búsquedas complejas


#-----------------------------Proovedor---------------------------------------
@login_required
def registrar_proveedor(request):
    # Validar permisos
    if not (request.user.is_superuser or request.user.rol in ['ADMIN', 'BODEGA']):
        return redirect('redireccion_rol')

    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            # Por ahora lo mandamos al dashboard, luego crearemos la lista de proveedores
            return redirect('dashboard_admin') 
    else:
        form = ProveedorForm()

    return render(request, 'usuarios/registro_proveedor.html', {'form': form})

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
# Asegúrate de tener esta importación arriba:
# from .models import Producto

@login_required
def lista_productos(request):
    # Obtenemos el valor de la barra de búsqueda (si existe)
    query = request.GET.get('q', '')
    if query:
        # Filtramos por nombre o código ignorando mayúsculas/minúsculas (icontains)
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query)
        )
    else:
        # Si no hay búsqueda, mostramos todo el inventario
        productos = Producto.objects.all()
        
    return render(request, 'usuarios/lista_productos.html', {
        'productos': productos,
        'query': query
    })

@login_required
def editar_producto(request, id):
    # 1. Seguridad (mantenla igual)
    if not (request.user.is_superuser or request.user.rol in ['ADMIN', 'BODEGA']):
        return redirect('redireccion_rol')

    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        form = EditarProductoForm(request.POST, instance=producto)
        
        # EL PUNTO CLAVE:
        if form.is_valid():
            form.save()
            return redirect('lista_productos') # Si es válido, redirige (302)
        else:
            # Si NO es válido, NO hagas nada más. 
            # El código debe salir del 'if' y llegar al 'render' de abajo (200)
            pass 
            
    else:
        form = EditarProductoForm(instance=producto)

    # Este render es el que recibe el test con el status 200
    return render(request, 'usuarios/editar_producto.html', {
        'form': form, 
        'producto': producto
    })

@login_required
def registrar_producto(request):
    if request.method == 'POST':
        form = RegistroProductoForm(request.POST)
        if form.is_valid():
            form.save()
            # OJO: Si aún no tienes la vista 'lista_productos', 
            # cámbiala temporalmente a 'dashboard_admin' para que no te dé error
            return redirect('registro_producto') 
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

#-----------------------------------------Cliente-----------------------------------
@login_required
def registrar_cliente(request):
    # Capa de seguridad: Solo ADMIN, VENDEDOR o Superusuarios pueden registrar clientes
    if not (request.user.is_superuser or request.user.rol in ['ADMIN', 'VENDEDOR']):
        return redirect('redireccion_rol')

    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirigimos al dashboard temporalmente tras un registro exitoso
            return redirect('dashboard_admin') 
    else:
        form = ClienteForm()

    return render(request, 'usuarios/registro_cliente.html', {'form': form})
#----------------------------------------Compra---------------------------------
def registrar_compra(request):
    if not (request.user.is_superuser or request.user.rol in ['ADMIN', 'BODEGA']):
        return redirect('redireccion_rol')

    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save()
            # Más adelante, aquí redirigiremos a "Añadir detalles a la compra" (HU-23)
            # Por ahora lo mandamos al dashboard
            return redirect('dashboard_admin')
    else:
        form = CompraForm()

    return render(request, 'usuarios/registro_compra.html', {'form': form})
#-------------------------------Deatlle comrap
def registrar_detalle_compra(request):

    if request.method == 'POST':
        form = RegistroDetalleCompraForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('registro_detalle_compra')

    else:
        form = RegistroDetalleCompraForm()

    return render(
        request,
        'usuarios/registro_detalle_compra.html',
        {'form': form}
    )

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