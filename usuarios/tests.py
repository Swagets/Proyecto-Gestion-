from django.test import TestCase, Client
from django.urls import reverse
# Asegúrate de importar los modelos que vayas a usar, como Usuario o Cliente
from .models import Usuario, Compra, Proveedor

class RegistrarCompraTests(TestCase):
    def setUp(self):
        # 1. Crear usuario autorizado
        self.user = Usuario.objects.create_user(username='admin', password='password', rol='ADMIN')
        
        # 2. Crear un proveedor necesario para la compra
        self.proveedor = Proveedor.objects.create(
            ruc='1712345678001', 
            nombre_empresa='Proveedor Test', 
            telefono='0999999999'
        )
        
        self.url = reverse('registrar_compra')

    def test_registro_compra_exitoso(self):
        """Verifica que se cree una compra correctamente con datos válidos"""
        self.client.login(username='admin', password='password')
        
        datos = {
            'proveedor': self.proveedor.id,
            'fecha': '2026-07-12',
            'numero_factura': 'FAC-001',
            'observacion': 'Compra de prueba',
            'estado': 'REGISTRADA'
        }
        
        response = self.client.post(self.url, datos)
        
        # Verificar que se redirija (a dashboard o lista) y que exista en BD
        self.assertEqual(Compra.objects.count(), 1)
        self.assertEqual(Compra.objects.first().numero_factura, 'FAC-001')

    def test_validacion_factura_duplicada(self):
        """Verifica que no se pueda registrar una factura con el mismo número"""
        self.client.login(username='admin', password='password')
        
        # Creamos una compra previa
        Compra.objects.create(
            proveedor=self.proveedor, 
            numero_factura='FAC-001', 
            estado='REGISTRADA'
        )
        
        datos_duplicados = {
            'proveedor': self.proveedor.id,
            'fecha': '2026-07-12',
            'numero_factura': 'FAC-001', # Mismo número
            'estado': 'REGISTRADA'
        }
        
        response = self.client.post(self.url, datos_duplicados)
        
        # El formulario debe ser inválido
        self.assertFormError(response.context['form'], 'numero_factura', 'Ya existe Compra con este Numero factura.')