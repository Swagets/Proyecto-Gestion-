import json
from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q, F, Sum
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .forms import (
    EditarUsuarioForm, RegistroProductoForm, EditarProductoForm,
    ProveedorForm, ClienteForm, CompraForm,
    LoteForm, UbicacionForm, VentaForm,
)
from .models import (
    Usuario, Producto, Proveedor, Cliente, Compra, DetalleCompra,
    Lote, Ubicacion, Venta, DetalleVenta,
)


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
    context = {
        'usuarios': Usuario.objects.all(),
        'productos_count': Producto.objects.filter(estado='ACTIVO').count(),
        'proveedores_count': Proveedor.objects.filter(estado='ACTIVO').count(),
        'clientes_count': Cliente.objects.filter(estado='ACTIVO').count(),
    }
    return render(request, 'usuarios/dashboard_admin.html', context)


@roles_permitidos('BODEGA')
def dashboard_bodega(request):
    productos = Producto.objects.filter(estado='ACTIVO')
    context = {
        'productos_count': productos.count(),
        'proveedores_count': Proveedor.objects.filter(estado='ACTIVO').count(),
        'compras_recientes': Compra.objects.order_by('-fecha')[:5],
    }
    return render(request, 'usuarios/dashboard_bodega.html', context)


@roles_permitidos('VENDEDOR')
def dashboard_vendedor(request):
    clientes = Cliente.objects.filter(estado='ACTIVO')
    context = {
        'clientes_count': clientes.count(),
        'clientes_recientes': clientes.order_by('-id')[:5],
        'productos_count': Producto.objects.filter(estado='ACTIVO').count(),
        'ventas_count': Venta.objects.count(),
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
            with transaction.atomic():
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


# ============================================
# VENTA
# ============================================
@roles_permitidos('ADMIN', 'VENDEDOR')
def registrar_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    venta = form.save()

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
                                    DetalleVenta.objects.create(
                                        venta=venta,
                                        producto=producto,
                                        cantidad=cant,
                                        precio_unitario=prec,
                                    )
                                    detalles_creados += 1
                            except (Producto.DoesNotExist, ValueError):
                                pass

                        i += 1

                    if detalles_creados == 0:
                        raise ValidationError('Debe agregar al menos un producto.')

                    # FIFO: descontar stock de lotes por caducidad más próxima
                    detalles = venta.detalles.select_related('producto')
                    for detalle in detalles:
                        producto = detalle.producto
                        restante = detalle.cantidad

                        lotes = Lote.objects.filter(
                            detalle_compra__producto=producto,
                            estado='ACTIVO',
                            cantidad_recibida__gt=0,
                        ).order_by('fecha_caducidad')

                        for lote in lotes:
                            if restante <= 0:
                                break
                            descuento = min(lote.cantidad_recibida, restante)
                            lote.cantidad_recibida -= descuento
                            lote.save(update_fields=['cantidad_recibida'])
                            restante -= descuento

                        if restante > 0:
                            raise ValidationError(
                                f'Stock insuficiente para "{producto.nombre}". '
                                f'Faltan {restante} unidad(es).'
                            )

                        producto.stock = Lote.objects.filter(
                            detalle_compra__producto=producto,
                            estado='ACTIVO',
                        ).aggregate(total=Sum('cantidad_recibida'))['total'] or 0
                        producto.save(update_fields=['stock'])

                    messages.success(
                        request,
                        f'Venta registrada exitosamente con {detalles_creados} producto(s).'
                    )
                    return redirect('redireccion_rol')

            except ValidationError as e:
                messages.error(request, e.message)
    else:
        form = VentaForm()

    productos = Producto.objects.filter(estado='ACTIVO').values('id', 'codigo', 'nombre', 'precio_venta')
    productos_json = json.dumps(list(productos), default=float)

    return render(request, 'usuarios/registro_venta.html', {
        'form': form,
        'productos_json': productos_json,
    })


# ============================================
# LOTES
# ============================================
@roles_permitidos('ADMIN', 'BODEGA')
def lista_compras_lotes(request):
    compras = Compra.objects.select_related('proveedor').order_by('-fecha')
    return render(request, 'usuarios/lista_compras_lotes.html', {
        'compras': compras,
    })


@roles_permitidos('ADMIN', 'BODEGA')
def lista_lotes_compra(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    detalles = compra.detalles.select_related('producto').prefetch_related('lotes')

    return render(request, 'usuarios/lista_lotes_compra.html', {
        'compra': compra,
        'detalles': detalles,
    })


@roles_permitidos('ADMIN', 'BODEGA')
def registrar_lote(request, detalle_id):
    detalle = get_object_or_404(DetalleCompra, id=detalle_id)

    cantidad_ya_registrada = sum(
        l.cantidad_recibida for l in detalle.lotes.all()
    )
    cantidad_disponible = detalle.cantidad - cantidad_ya_registrada

    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                lote = form.save(commit=False)
                lote.detalle_compra = detalle

                if lote.cantidad_recibida > cantidad_disponible:
                    form.add_error(
                        'cantidad_recibida',
                        f'La cantidad no puede exceder la disponible ({cantidad_disponible}).'
                    )
                else:
                    lote.save()

                    producto = detalle.producto
                    producto.stock = sum(
                        l.cantidad_recibida
                        for l in Lote.objects.filter(
                            detalle_compra__producto=producto
                        )
                    )
                    producto.save(update_fields=['stock'])

                    messages.success(
                        request,
                        f'Lote {lote.numero_lote} registrado exitosamente. Stock actualizado.'
                    )
                    return redirect('lista_lotes_compra', compra_id=detalle.compra.id)
    else:
        form = LoteForm()

    return render(request, 'usuarios/registrar_lote.html', {
        'form': form,
        'detalle': detalle,
        'cantidad_ya_registrada': cantidad_ya_registrada,
        'cantidad_disponible': cantidad_disponible,
    })


@roles_permitidos('ADMIN', 'BODEGA')
def crear_ubicacion(request):
    detalle_id = request.GET.get('detalle_id') or request.POST.get('detalle_id')

    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            ubicacion = form.save()
            messages.success(
                request,
                f'Ubicación {ubicacion.codigo} creada exitosamente.'
            )
            if detalle_id:
                return redirect('registrar_lote', detalle_id=int(detalle_id))
            return redirect('redireccion_rol')
    else:
        form = UbicacionForm()

    return render(request, 'usuarios/registro_ubicacion.html', {
        'form': form,
        'detalle_id': detalle_id,
    })


# ============================================
# INVENTARIO
# ============================================
@roles_permitidos('ADMIN', 'BODEGA')
def lista_inventario(request):
    hoy = timezone.now().date()
    limite_caducidad = hoy + timedelta(days=30)

    lotes = Lote.objects.select_related(
        'detalle_compra__producto',
        'ubicacion',
    ).filter(detalle_compra__producto__estado='ACTIVO')

    query = request.GET.get('q', '')
    if query:
        lotes = lotes.filter(
            detalle_compra__producto__nombre__icontains=query
        )

    ubicacion_id = request.GET.get('ubicacion', '')
    if ubicacion_id:
        lotes = lotes.filter(ubicacion_id=ubicacion_id)

    estado = request.GET.get('estado', '')
    if estado:
        lotes = lotes.filter(estado=estado)

    stock_bajo = request.GET.get('stock_bajo', '')
    agotados = request.GET.get('agotados', '')
    caducar = request.GET.get('caducar', '')

    if stock_bajo == '1':
        lotes = lotes.filter(
            detalle_compra__producto__stock__gt=0,
            detalle_compra__producto__stock__lte=F('detalle_compra__producto__stock_minimo'),
        )
    elif agotados == '1':
        lotes = lotes.filter(detalle_compra__producto__stock=0)
    elif caducar:
        dias = int(caducar) if caducar.isdigit() else 30
        limite = hoy + timedelta(days=dias)
        lotes = lotes.filter(
            fecha_caducidad__lte=limite,
            fecha_caducidad__gte=hoy,
        )

    ordenar = request.GET.get('ordenar', 'nombre')
    orden_map = {
        'nombre': 'detalle_compra__producto__nombre',
        'stock': 'detalle_compra__producto__stock',
        'caducidad': 'fecha_caducidad',
    }
    campo_orden = orden_map.get(ordenar, 'detalle_compra__producto__nombre')
    lotes = lotes.order_by(campo_orden)

    ubicaciones = Ubicacion.objects.all().order_by('codigo')

    base_productos = Producto.objects.filter(estado='ACTIVO')
    total_productos = base_productos.count()

    disponibles = base_productos.filter(
        stock__gt=F('stock_minimo')
    ).count()

    productos_stock_bajo = base_productos.filter(
        stock__gt=0,
        stock__lte=F('stock_minimo'),
    ).count()

    productos_caducar = base_productos.filter(
        detallecompra__lotes__fecha_caducidad__lte=limite_caducidad,
        detallecompra__lotes__fecha_caducidad__gte=hoy,
        detallecompra__lotes__estado='ACTIVO',
    ).distinct().count()

    return render(request, 'usuarios/inventario.html', {
        'lotes': lotes,
        'ubicaciones': ubicaciones,
        'query': query,
        'ubicacion_seleccionada': ubicacion_id,
        'estado_seleccionado': estado,
        'ordenar': ordenar,
        'hoy': hoy,
        'limite_caducidad': limite_caducidad,
        'stock_bajo_activo': stock_bajo == '1',
        'agotados_activo': agotados == '1',
        'caducar_activo': caducar != '',
        'total_productos': total_productos,
        'disponibles': disponibles,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_caducar': productos_caducar,
    })


# ============================================
# CERRAR SESIÓN
# ============================================
@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('login')
