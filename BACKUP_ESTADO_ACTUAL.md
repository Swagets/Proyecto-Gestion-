# BACKUP - Estado Actual del Proyecto PowerMedical
# Generado antes de iniciar rediseño de interfaz

## URLS EXISTENTES (usuarios/urls.py)
- login/ -> LoginView (template: login.html) -> name='login'
- logout/ -> LogoutView (next_page='login') -> name='logout'
- redireccion/ -> redireccion_por_rol -> name='redireccion_rol'
- registrar/ -> registro_usuario -> name='registro_usuario'
- editar/<int:id>/ -> editar_usuario -> name='editar_usuario'
- productos/registrar/ -> registrar_producto -> name='registro_producto'
- productos/editar/<int:id>/ -> editar_producto -> name='editar_producto'
- productos/lista/ -> lista_productos -> name='lista_productos'
- proveedores/registrar/ -> registrar_proveedor -> name='registrar_proveedor'
- clientes/registrar/ -> registrar_cliente -> name='registrar_cliente'
- compras/registrar/ -> registrar_compra -> name='registrar_compra'
- compras/detalle/registrar/ -> registrar_detalle_compra -> name='registro_detalle_compra'
- dashboard/admin/ -> dashboard_admin -> name='dashboard_admin'
- dashboard/bodega/ -> dashboard_bodega -> name='dashboard_bodega'
- dashboard/vendedor/ -> dashboard_vendedor -> name='dashboard_vendedor'

## URLS RAIZ (config/urls.py)
- admin/ -> admin.site.urls
- usuarios/ -> include('usuarios.urls')
- dashboard/admin/ -> views.dashboard_admin -> name='dashboard_admin'
- dashboard/bodega/ -> views.dashboard_bodega -> name='dashboard_bodega'
- dashboard/vendedor/ -> views.dashboard_vendedor -> name='dashboard_vendedor'

## VISTAS (views.py)
### registrar_proveedor
- @login_required
- Valida permisos: is_superuser or rol in ['ADMIN', 'BODEGA']
- POST: ProveedorForm -> save -> redirect('dashboard_admin')
- GET: render registro_proveedor.html con form vacío

### registro_usuario
- Sin @login_required
- POST: RegistroUsuarioForm -> save -> redirect('registro_usuario')
- GET: render registro_usuario.html con form vacío

### lista_productos
- @login_required
- GET con param 'q': filtra Producto por nombre/codigo icontains
- Sin 'q': muestra todos
- render lista_productos.html con productos y query

### editar_producto
- @login_required
- Valida permisos: is_superuser or rol in ['ADMIN', 'BODEGA']
- POST: EditarProductoForm(instance=producto) -> save -> redirect('lista_productos')
- GET: render editar_producto.html con form y producto
- Usa get_object_or_404

### registrar_producto
- @login_required
- POST: RegistroProductoForm -> save -> redirect('registro_producto')
- GET: render registro_producto.html con form vacío

### editar_usuario
- @login_required
- Valida permisos: is_superuser or rol == 'ADMIN'
- POST: EditarUsuarioForm(instance=usuario) -> save -> redirect('dashboard_admin')
- GET: render editar_usuario.html con form y usuario_editado
- Usa get_object_or_404

### registrar_cliente
- @login_required
- Valida permisos: is_superuser or rol in ['ADMIN', 'VENDEDOR']
- POST: ClienteForm -> save -> redirect('dashboard_admin')
- GET: render registro_cliente.html con form vacío

### registrar_compra
- Sin @login_required verificado (falta en código original)
- Valida permisos: is_superuser or rol in ['ADMIN', 'BODEGA']
- POST: CompraForm -> save -> redirect('dashboard_admin')
- GET: render registro_compra.html con form vacío

### registrar_detalle_compra
- Sin @login_required
- Sin validación de permisos
- POST: RegistroDetalleCompraForm -> save -> redirect('registro_detalle_compra')
- GET: render registro_detalle_compra.html con form vacío

### redireccion_por_rol
- @login_required
- is_superuser or ADMIN -> redirect('dashboard_admin')
- BODEGA -> redirect('dashboard_bodega')
- VENDEDOR -> redirect('dashboard_vendedor')
- otro -> HttpResponse("Rol no reconocido")

### dashboard_admin
- @login_required
- Valida permisos: is_superuser or rol == 'ADMIN'
- Obtiene todos los Usuario.objects.all()
- render dashboard_admin.html con usuarios

### dashboard_bodega
- @login_required
- HttpResponse("Dashboard Bodeguero")

### dashboard_vendedor
- @login_required
- HttpResponse("Dashboard Vendedor")

## FORMULARIOS (forms.py)
### RegistroUsuarioForm
- fields: first_name, last_name, username, email, password, confirm_password, rol
- Valida: passwords coinciden + validate_password de Django
- save: set_password() then save()

### EditarUsuarioForm
- fields: first_name, last_name, username (disabled), email, rol

### ClienteForm
- fields: nombre, cedula_ruc, telefono, correo, direccion, estado
- Valida: nombre (solo letras), cedula_ruc (10 o 13 digitos), telefono (9-15 digitos)

### RegistroProductoForm
- fields: codigo, nombre, descripcion, categoria, laboratorio, unidad_medida, temperatura, precio_compra, precio_venta, iva, estado
- Valida: codigo único, precio_compra > 0, precio_venta > 0, precio_venta >= precio_compra

### EditarProductoForm
- fields: codigo (readonly), nombre, descripcion, categoria, laboratorio, unidad_medida, temperatura, precio_compra, precio_venta, iva, estado

### ProveedorForm
- fields: ruc, nombre_empresa, contacto, telefono, correo, direccion, estado
- Valida: ruc (solo numeros, 13 digitos)

### CompraForm
- fields: proveedor, fecha, numero_factura, observacion, estado
- NO MODIFICAR - debe permanecer intacto

### RegistroDetalleCompraForm
- fields: compra, producto, cantidad, precio_unitario
- Sin validaciones custom

## TEMPLATES EXISTENTES
- base.html: Bootstrap 5 CDN, container mt-4, block content
- login.html: HTML standalone, form as_p, boton "Ingresar"
- dashboard_admin.html: extends base, container, tabla usuarios, boton registrar
- registro_usuario.html: extends base, form loop con labels y errores
- editar_usuario.html: extends base, form as_p, boton actualizar
- registro_producto.html: extends base, card con form as_p
- lista_productos.html: extends base, card con buscador y tabla
- editar_producto.html: extends base, card con form as_p
- registro_proveedor.html: extends base, card con form iterado
- registro_cliente.html: extends base, card con form iterado
- registro_compra.html: extends base, card con form manual por campos
- registro_detalle_compra.html: extends base, card con form as_p

## MODELOS (NO MODIFICAR)
- Usuario (AbstractUser): rol
- Producto: codigo, nombre, descripcion, categoria, laboratorio, unidad_medida, temperatura, precio_compra, precio_venta, iva, estado
- Proveedor: ruc, nombre_empresa, contacto, telefono, correo, direccion, estado
- Cliente: nombre, cedula_ruc, telefono, correo, direccion, estado
- Compra: proveedor(FK), fecha, numero_factura, observacion, estado
- DetalleCompra: compra(FK), producto(FK), cantidad, precio_unitario, subtotal(editable=False, calculado en save)

## SETTINGS
- AUTH_USER_MODEL = 'usuarios.Usuario'
- LOGIN_REDIRECT_URL = '/admin/'
- LOGIN_URL = 'login'
- STATIC_URL = 'static/'
- APP_DIRS = True (templates en usuarios/templates/)
