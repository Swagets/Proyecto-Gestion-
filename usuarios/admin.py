from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Producto, Proveedor, Cliente

admin.site.register(Usuario, UserAdmin)
admin.site.register(Producto)
admin.site.register(Proveedor)
admin.site.register(Cliente)