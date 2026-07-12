from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario
from django.test import TestCase, Client, override_settings # <--- 1. Importa override_settings
from django.urls import reverse
from .models import Usuario

# 2. Obliga a usar tus URLs reales
@override_settings(ROOT_URLCONF='config.urls') 
class TestRedireccionRoles(TestCase):

    def setUp(self):
        # Creamos tres usuarios de prueba con diferentes roles
        self.admin = Usuario.objects.create_user(username='admin_test', password='password123', rol='ADMIN')
        self.bodeguero = Usuario.objects.create_user(username='bodega_test', password='password123', rol='BODEGA')
        self.vendedor = Usuario.objects.create_user(username='vendedor_test', password='password123', rol='VENDEDOR')
        self.client = Client()

    def test_redireccion_admin(self):
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('redireccion_rol'))
        # Verificamos que el admin sea enviado al admin de Django
        self.assertRedirects(response, '/dashboard/admin/')

    def test_redireccion_bodega(self):
        self.client.login(username='bodega_test', password='password123')
        response = self.client.get(reverse('redireccion_rol'))
        # Verificamos que sea enviado a /bodega/
        self.assertEqual(response.status_code, 302)
        self.assertIn('/bodega/', response.url)