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