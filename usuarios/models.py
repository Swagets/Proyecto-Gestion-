from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

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
class Proveedor(models.Model):

    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    ruc = models.CharField(
        max_length=13, 
        unique=True, 
        verbose_name="RUC"
    )
    
    nombre_empresa = models.CharField(
        max_length=150, 
        verbose_name="Nombre de la Empresa o Razón Social"
    )
    
    contacto = models.CharField(
        max_length=100, 
        verbose_name="Nombre del Contacto"
    )
    
    telefono = models.CharField(
        max_length=15, 
        verbose_name="Teléfono"
    )
    
    correo = models.EmailField(
        blank=True, 
        null=True, 
        verbose_name="Correo Electrónico"
    )
    
    direccion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Dirección"
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='ACTIVO',
        verbose_name="Estado"
    )

    def __str__(self):
        return f"{self.nombre_empresa} - {self.ruc}"

class Cliente(models.Model):

    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=150)
    cedula_ruc = models.CharField(max_length=13, unique=True)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255)
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='ACTIVO'
    )

    def __str__(self):
        return self.nombre
    
class Compra(models.Model):

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT
    )

    fecha = models.DateField(default=timezone.now)

    numero_factura = models.CharField(
        max_length=30,
        unique=True
    )

    observacion = models.TextField(
        blank=True,
        null=True
    )

    ESTADOS = [
        ('REGISTRADA', 'Registrada'),
        ('ANULADA', 'Anulada'),
    ]

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='REGISTRADA'
    )

    def __str__(self):
        return f"Compra {self.numero_factura}"

class DetalleCompra(models.Model):

    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT
    )

    cantidad = models.PositiveIntegerField()

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.compra.numero_factura} - {self.producto.nombre}"