from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('BODEGA', 'Bodeguero'),
        ('VENDEDOR', 'Vendedor'),
    ]
    
    rol = models.CharField(
        max_length=15,
        choices=ROLES,
        default='VENDEDOR'
    )

    
class Producto(models.Model):

    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    categoria = models.CharField(max_length=100)
    laboratorio = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=50)

    temperatura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Temperatura de almacenamiento en °C"
    )

    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)

    iva = models.DecimalField(max_digits=5, decimal_places=2)

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='ACTIVO'
    )

    def __str__(self):
        return self.nombre