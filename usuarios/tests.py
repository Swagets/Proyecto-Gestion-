from django.test import TestCase
from .models import Producto
from .forms import RegistroProductoForm

class ProductoFormTest(TestCase):

    def setUp(self):
        # Creamos un producto base para probar la validación de duplicidad
        self.producto_existente = Producto.objects.create(
            codigo="PROD001",
            nombre="Producto Base",
            precio_compra=10.00,
            precio_venta=20.00
        )

    def test_codigo_unico(self):
        """Prueba que no se pueda registrar un código que ya existe."""
        form = RegistroProductoForm(data={
            'codigo': 'PROD001', # El mismo código creado en setUp
            'nombre': 'Otro',
            'precio_compra': 5.00,
            'precio_venta': 10.00
        })
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)

    def test_precio_venta_menor_que_compra(self):
        """Prueba la validación cruzada: venta no puede ser menor a compra."""
        form = RegistroProductoForm(data={
            'codigo': 'PROD002',
            'nombre': 'Test Precio',
            'precio_compra': 50.00,
            'precio_venta': 30.00 # ¡Error! Venta < Compra
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors) # Los errores de clean() general van en __all__

    def test_precios_positivos(self):
        """Prueba que los precios deban ser mayores a 0."""
        form = RegistroProductoForm(data={
            'codigo': 'PROD003',
            'nombre': 'Test Negativo',
            'precio_compra': -1.00,
            'precio_venta': -5.00
        })
        self.assertFalse(form.is_valid())
        self.assertIn('precio_compra', form.errors)
        self.assertIn('precio_venta', form.errors)

    def test_formulario_valido(self):
        """Prueba que un formulario con datos correctos pase."""
        form = RegistroProductoForm(data={
            'codigo': 'PROD999',
            'nombre': 'Producto Correcto',
            'precio_compra': 10.00,
            'precio_venta': 15.00
        })
        self.assertTrue(form.is_valid())