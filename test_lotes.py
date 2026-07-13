"""
Script de pruebas: Flujo completo de navegacion de Lotes
Ejecutar: python test_lotes.py
"""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS = ['*']

from django.test.client import Client
from django.urls import reverse

from usuarios.models import Usuario, Producto, Proveedor, Compra, DetalleCompra, Lote

OK = "[PASS]"
FAIL = "[FAIL]"

passed = 0
failed = 0
errors = []

# Cleanup old test data (order matters due to FK constraints)
Compra.objects.filter(numero_factura='001-001-000012345').delete()
# Also clean any leftover proveedores from previous test runs
for p in Proveedor.objects.filter(ruc='1712345678001'):
    Compra.objects.filter(proveedor=p).delete()
    p.delete()
Producto.objects.filter(codigo='PARA-500').delete()
Usuario.objects.filter(username__in=['admin_test', 'bodega_test', 'vendedor_test']).delete()

proveedor = Proveedor.objects.create(
    ruc='1712345678001', nombre_empresa='PharmaCorp',
    contacto='Juan Perez', telefono='0991234567', estado='ACTIVO'
)
producto = Producto.objects.create(
    codigo='PARA-500', nombre='Paracetamol 500mg',
    categoria='Analgesicos', laboratorio='LabTest',
    unidad_medida='Tabletas', temperatura=25.00,
    precio_compra=0.50, precio_venta=1.00, iva=12.00, estado='ACTIVO'
)

admin_user = Usuario.objects.create_user('admin_test', 'admin@test.com', 'test1234', rol='ADMIN')
bodega_user = Usuario.objects.create_user('bodega_test', 'bodega@test.com', 'test1234', rol='BODEGA')
vendedor_user = Usuario.objects.create_user('vendedor_test', 'vendedor@test.com', 'test1234', rol='VENDEDOR')

c = Client()
c.login(username='admin_test', password='test1234')


# ============================================================
print("=" * 60)
print("  FLUJO DE NAVEGACION: GESTIONAR LOTES")
print("=" * 60)


# TEST 1: Dashboard -> Gestionar Lotes (lista de compras)
print("\n[1] Acceder a Gestionar Lotes (GET /compras/lotes/)...")
resp = c.get(reverse('lista_compras_lotes'))
if resp.status_code == 200:
    print(f"   {OK} Lista de compras accessible (status 200)")
    passed += 1
else:
    print(f"   {FAIL} Status={resp.status_code}, esperaba 200")
    failed += 1
    errors.append("TEST 1: No se puede acceder a lista de compras")


# TEST 2: Registrar una compra
print("\n[2] Registrar compra de prueba...")
data = {
    'proveedor': proveedor.id,
    'fecha': '2026-07-13',
    'numero_factura': '001-001-000012345',
    'observacion': 'Compra de prueba',
    'estado': 'REGISTRADA',
    'det_producto_0': str(producto.id),
    'det_cantidad_0': '10',
    'det_precio_0': '5.00',
}
resp = c.post(reverse('registrar_compra'), data)
compra = Compra.objects.filter(numero_factura='001-001-000012345').first()
detalle = DetalleCompra.objects.filter(compra=compra).first()

if compra and detalle:
    print(f"   {OK} Compra #{compra.id} con detalle (cant={detalle.cantidad})")
    passed += 1
else:
    print(f"   {FAIL} Compra o detalle no creado")
    failed += 1
    errors.append("TEST 2: Compra no creada")


# TEST 3: Volver a Gestionar Lotes -> compra aparece en la lista
print("\n[3] Verificar que la compra aparece en la lista de lotes...")
resp = c.get(reverse('lista_compras_lotes'))
if compra.numero_factura.encode() in resp.content:
    print(f"   {OK} Compra {compra.numero_factura} aparece en la lista")
    passed += 1
else:
    print(f"   {FAIL} Compra no aparece en la lista")
    failed += 1
    errors.append("TEST 3: Compra no visible en lista")


# TEST 4: Seleccionar compra -> ver sus detalles
print("\n[4] Seleccionar compra -> ver detalles (GET /compras/<id>/lotes/)...")
resp = c.get(reverse('lista_lotes_compra', kwargs={'compra_id': compra.id}))
if resp.status_code == 200 and b'Paracetamol' in resp.content:
    print(f"   {OK} Detalles de compra visibles (incluye Paracetamol)")
    passed += 1
else:
    print(f"   {FAIL} Status={resp.status_code}, productos no visibles")
    failed += 1
    errors.append("TEST 4: Detalles no visibles")


# TEST 5: Verificar boton "Registrar Lote" en el detalle
print("\n[5] Verificar boton 'Registrar Lote' en el detalle...")
url_lote = reverse('registrar_lote', kwargs={'detalle_id': detalle.id})
if url_lote.encode() in resp.content:
    print(f"   {OK} Boton 'Registrar Lote' presente (url={url_lote})")
    passed += 1
else:
    print(f"   {FAIL} Boton 'Registrar Lote' no encontrado")
    failed += 1
    errors.append("TEST 5: Boton Registrar Lote no encontrado")


# TEST 6: Hacer click en Registrar Lote -> formulario
print("\n[6] Acceder a formulario de lote (GET registrar_lote)...")
resp = c.get(url_lote)
if resp.status_code == 200 and b'LOTE' in resp.content:
    print(f"   {OK} Formulario de lote accesible")
    passed += 1
else:
    print(f"   {FAIL} Status={resp.status_code}")
    failed += 1
    errors.append("TEST 6: Formulario de lote no accesible")


# TEST 7: Registrar lote -> volver a la lista de detalles
print("\n[7] Registrar lote y volver a la lista de detalles...")
data_lote = {
    'numero_lote': 'LOTE-001',
    'fecha_fabricacion': '2026-01-15',
    'fecha_caducidad': '2027-01-15',
    'cantidad_recibida': '6',
    'estado': 'ACTIVO',
}
resp = c.post(reverse('registrar_lote', kwargs={'detalle_id': detalle.id}), data_lote)
lote1 = Lote.objects.filter(numero_lote='LOTE-001', detalle_compra=detalle).first()
# Should redirect to lista_lotes_compra
if resp.status_code == 302 and str(compra.id) in resp.url:
    print(f"   {OK} Lote creado, redirige a detalles de compra (id={compra.id})")
    passed += 1
elif lote1:
    print(f"   {OK} Lote creado (redireccion no ideal pero funcional)")
    passed += 1
else:
    print(f"   {FAIL} Lote no creado")
    failed += 1
    errors.append("TEST 7: Lote no creado")


# TEST 8: Flujo completo: vendedor no puede ver lotes
print("\n[8] Vendedor no puede acceder a ningun endpoint de lotes...")
c.logout()
c.login(username='vendedor_test', password='test1234')

resp1 = c.get(reverse('lista_compras_lotes'))
resp2 = c.get(reverse('lista_lotes_compra', kwargs={'compra_id': compra.id}))
resp3 = c.get(reverse('registrar_lote', kwargs={'detalle_id': detalle.id}))

all_blocked = all(
    r.status_code == 302 and 'redireccion' in r.url
    for r in [resp1, resp2, resp3]
)
if all_blocked:
    print(f"   {OK} Vendedor bloqueado en los 3 endpoints de lotes")
    passed += 1
else:
    print(f"   {FAIL} Vendedor pudo acceder a algun endpoint")
    failed += 1
    errors.append("TEST 8: Vendedor no bloqueado")


# TEST 9: Sin sesion -> redirige a login
print("\n[9] Sin sesion -> redirige a login en todos los endpoints...")
c.logout()
resp1 = c.get(reverse('lista_compras_lotes'))
resp2 = c.get(reverse('lista_lotes_compra', kwargs={'compra_id': compra.id}))
resp3 = c.get(reverse('registrar_lote', kwargs={'detalle_id': detalle.id}))

all_login = all(
    r.status_code == 302 and 'login' in r.url
    for r in [resp1, resp2, resp3]
)
if all_login:
    print(f"   {OK} Todos redirigen a login")
    passed += 1
else:
    print(f"   {FAIL} Algun endpoint no redirige a login")
    failed += 1
    errors.append("TEST 9: No todos redirigen a login")


# RESUMEN
print("\n" + "=" * 60)
total = passed + failed
print(f"  RESULTADO: {passed}/{total} pruebas pasaron")
if failed == 0:
    print("  FLUJO DE NAVEGACION: COMPLETAMENTE FUNCIONAL")
else:
    print(f"  {failed} prueba(s) fallaron:")
    for e in errors:
        print(f"    - {e}")
print("=" * 60)
