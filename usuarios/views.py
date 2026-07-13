import json
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q

from .forms import (
    EditarUsuarioForm, RegistroProductoForm, EditarProductoForm,
    ProveedorForm, ClienteForm, CompraForm, RegistroDetalleCompraForm,
)
from .models import Usuario, Producto, Proveedor, Cliente, Compra, DetalleCompra


# ============================================
# DECORADOR REUTILIZABLE
# ============================================
def roles_permitidos(*roles):
    """
    Decorador que combina @login_required con verificación de rol.
    Los superusers siempre tienen acceso.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser or request.user.rol in roles:
                return view_func(request, *args, **kwargs)
            return redirect('redireccion_rol')
        return wrapper
    return decorator


# ============================================
# REDIRECCIÓN CENTRALIZADA POR ROL
# ============================================
@login_required
def redireccion_por_rol(request):
    if request.user.is_superuser or request.user.rol == 'ADMIN':
        return redirect('dashboard_admin')
    elif request.user.rol == 'BODEGA':
        return redirect('dashboard_bodega')
    elif request.user.rol == 'VENDEDOR':
        return redirect('dashboard_vendedor')
    else:
        return HttpResponse("Rol no reconocido")


# ============================================
# DASHBOARDS
# ============================================
@roles_permitidos('ADMIN')
def dashboard_admin(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/dashboard_admin.html', {'usuarios': usuarios})


@roles_permitidos('BODEGA')
def dashboard_bodega(request):
    productos = Producto.objects.filter(estado='ACTIVO')
    compras_recientes = Compra.objects.order_by('-fecha')[:5]
    context = {
        'productos_count': productos.count(),
        'compras_recientes': compras_recientes,
    }
    return render(request, 'usuarios/dashboard_bodega.html', context)


@roles_permitidos('VENDEDOR')
def dashboard_vendedor(request):
    clientes = Cliente.objects.filter(estado='ACTIVO')
    context = {
        'clientes_count': clientes.count(),
        'clientes_recientes': clientes.order_by('-id')[:5],
    }
    return render(request, 'usuarios/dashboard_vendedor.html', context)


# ============================================
# USUARIO
# ============================================
@roles_permitidos('ADMIN')
def registro_usuario(request):
    from .forms import RegistroUsuarioForm

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registro_usuario')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'usuarios/registro_usuario.html', {'form': form})


@roles_permitidos('ADMIN')
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('redireccion_rol')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {
        'form': form,
        'usuario_editado': usuario,
    })


# ============================================
# PRODUCTO
# ============================================
@roles_permitidos('ADMIN', 'BODEGA', 'VENDEDOR')
def lista_productos(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query)
        )
    else:
        productos = Producto.objects.all()

    return render(request, 'usuarios/lista_productos.html', {
        'productos': productos,
        'query': query,
    })


@roles_permitidos('ADMIN', 'BODEGA')
def registrar_producto(request):
    if request.method == 'POST':
        form = RegistroProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registro_producto')
    else:
        form = RegistroProductoForm()

    return render(request, 'usuarios/registro_producto.html', {'form': form})


@roles_permitidos('ADMIN', 'BODEGA')
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        form = EditarProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = EditarProductoForm(instance=producto)

    return render(request, 'usuarios/editar_producto.html', {
        'form': form,
        'producto': producto,
    })


# ============================================
# PROVEEDOR
# ============================================
@roles_permitidos('ADMIN', 'BODEGA')
def registrar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('redireccion_rol')
    else:
        form = ProveedorForm()

    return render(request, 'usuarios/registro_proveedor.html', {'form': form})


# ============================================
# CLIENTE
# ============================================
@roles_permitidos('ADMIN', 'VENDEDOR')
def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('redireccion_rol')
    else:
        form = ClienteForm()

    return render(request, 'usuarios/registro_cliente.html', {'form': form})


# ============================================
# COMPRA
# ============================================
@roles_permitidos('ADMIN', 'BODEGA')
def registrar_compra(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save()

            detalles_creados = 0
            i = 0
            while True:
                producto_id = request.POST.get(f'det_producto_{i}')
                cantidad = request.POST.get(f'det_cantidad_{i}')
                precio = request.POST.get(f'det_precio_{i}')

                if producto_id is None:
                    break

                if producto_id and cantidad and precio:
                    try:
                        producto = Producto.objects.get(id=int(producto_id))
                        cant = int(cantidad)
                        prec = float(precio)

                        if cant > 0 and prec > 0:
                            DetalleCompra.objects.create(
                                compra=compra,
                                producto=producto,
                                cantidad=cant,
                                precio_unitario=prec,
                            )
                            detalles_creados += 1
                    except (Producto.DoesNotExist, ValueError):
                        pass

                i += 1

            if detalles_creados > 0:
                messages.success(request, f'Compra registrada exitosamente con {detalles_creados} producto(s).')
            else:
                messages.warning(request, 'Compra registrada sin detalles.')

            return redirect('redireccion_rol')
    else:
        form = CompraForm()

    productos = Producto.objects.filter(estado='ACTIVO').values('id', 'codigo', 'nombre', 'precio_venta')
    productos_json = json.dumps(list(productos), default=float)

    return render(request, 'usuarios/registro_compra.html', {
        'form': form,
        'productos_json': productos_json,
    })


@roles_permitidos('ADMIN', 'BODEGA')
def registrar_detalle_compra(request):
    return redirect('registrar_compra')
