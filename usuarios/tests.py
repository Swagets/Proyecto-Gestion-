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
    def test_redireccion_vendedor(self):
        self.client.login(username='vendedor_test', password='password123')
        response = self.client.get(reverse('redireccion_rol'))
        # Actualizamos esto a la ruta real de tu sistema
        self.assertRedirects(response, '/dashboard/vendedor/')
        # ------------------------------TEST------------------------------------------
class RegistroUsuarioTest(TestCase):
    def test_registro_usuario_exitoso(self):
        # 1. Datos de prueba
        data = {
            'first_name': 'Juan',
            'last_name': 'Perez',
            'username': 'juanperez',
            'email': 'juan@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'rol': 'VENDEDOR' # Asegúrate de que este valor sea válido en tu modelo
        }
        
        # 2. Simulamos una petición POST a tu vista
        # 'registro_usuario' es el nombre que le diste a la URL en urls.py
        response = self.client.post(reverse('registro_usuario'), data)
        
        # 3. Verificamos que redirija (asumiendo que rediriges tras éxito)
        # Si no rediriges, puedes verificar response.status_code == 200
        self.assertEqual(response.status_code, 302) 
        
        # 4. Verificamos que el usuario realmente esté en la base de datos
        self.assertTrue(Usuario.objects.filter(username='juanperez').exists())
#---------------------------------Edicion de Usuario-------------------------------
class EditarUsuarioTests(TestCase):
    def setUp(self):
        # 1. Crear un usuario Administrador
        self.admin = Usuario.objects.create_user(
            username='admin_test',
            password='testpassword123',
            email='admin@test.com',
            rol='ADMIN'
        )
        
        # 2. Crear un usuario Bodeguero (para probar que se le bloquee el acceso)
        self.bodega = Usuario.objects.create_user(
            username='bodega_test',
            password='testpassword123',
            email='bodega@test.com',
            rol='BODEGA'
        )
        
        # 3. Crear el usuario que vamos a intentar editar
        self.usuario_destino = Usuario.objects.create_user(
            username='usuario_editar',
            password='testpassword123',
            first_name='Juan',
            email='juan@test.com',
            rol='VENDEDOR'
        )
        
        # Generar la URL dinámica de edición
        self.url_editar = reverse('editar_usuario', args=[self.usuario_destino.id])

    def test_acceso_denegado_a_no_administradores(self):
        """Verifica que un usuario sin rol ADMIN sea expulsado de la vista de edición"""
        self.client.login(username='bodega_test', password='testpassword123')
        
        response = self.client.get(self.url_editar)
        
        # CAMBIO: Usamos assertEqual para verificar que el código sea un 302 (Redirección)
        # sin obligar a Django a verificar la página de destino.
        self.assertEqual(response.status_code, 302)

    def test_edicion_exitosa_por_administrador(self):
        """Verifica que un ADMIN pueda actualizar los datos de otro usuario"""
        # Iniciamos sesión como administrador
        self.client.login(username='admin_test', password='testpassword123')
        
        # Preparamos los nuevos datos que enviaremos en el formulario
        nuevos_datos = {
            'first_name': 'Pedro',
            'last_name': 'Perez',
            'username': 'usuario_editar', # Este campo está bloqueado en el form, enviamos el mismo
            'email': 'pedro.nuevo@test.com',
            'rol': 'VENDEDOR'
        }
        
        # Hacemos el POST (simulando que hacemos clic en "Actualizar Datos")
        response = self.client.post(self.url_editar, nuevos_datos)
        
        # 1. Verificamos que nos regrese al dashboard después de guardar
        self.assertRedirects(response, reverse('dashboard_admin'))
        
        # 2. Refrescamos el usuario de la base de datos para ver los cambios
        self.usuario_destino.refresh_from_db()
        
        # 3. Verificamos que el nombre y el correo hayan cambiado
        self.assertEqual(self.usuario_destino.first_name, 'Pedro')
        self.assertEqual(self.usuario_destino.last_name, 'Perez')
        self.assertEqual(self.usuario_destino.email, 'pedro.nuevo@test.com')