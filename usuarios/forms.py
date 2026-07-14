from django import forms
from .models import Usuario, Producto, Proveedor, Cliente, Compra, DetalleCompra, Lote, Ubicacion, Venta, DetalleVenta
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'rol']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    # 1. Validar que las contraseñas coincidan
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # 1. Validar que coincidan
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")

        # 2. Validar política de Django (longitud, complejidad)
        if password:
            try:
                validate_password(password)
            except forms.ValidationError as e:
                self.add_error('password', e)

        return cleaned_data

    # 2. Guardar de forma segura
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario
    
    #-----------------------------------Edicion de Uusario-------------------------------------
class EditarUsuarioForm(forms.ModelForm):
    # Redefinimos el campo para que sea de solo lectura (deshabilitado)
    username = forms.CharField(
        disabled=True, 
        widget=forms.TextInput(attrs={'class': 'form-control text-muted'})
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'username', 'email', 'rol']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }

#-------------------------Cliente----------------------------

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'cedula_ruc', 'telefono', 'correo', 'direccion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}),
            'cedula_ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10 (Cédula) o 13 (RUC) dígitos'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0987654321'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    # 1. Validación del Nombre
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        # Solo permite letras (incluyendo tildes y eñes) y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise ValidationError("El nombre solo debe contener letras y espacios.")
        return nombre

    # 2. Validación de Cédula/RUC (La que ya teníamos)
    def clean_cedula_ruc(self):
        cedula_ruc = self.cleaned_data.get('cedula_ruc')
        if not cedula_ruc.isdigit():
            raise ValidationError("Este campo debe contener únicamente números.")
        if len(cedula_ruc) not in [10, 13]:
            raise ValidationError("La Cédula debe tener 10 dígitos y el RUC 13 dígitos.")
        return cedula_ruc

    # 3. Validación del Teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise ValidationError("El teléfono solo debe contener números.")
        if len(telefono) < 9 or len(telefono) > 15:
            raise ValidationError("El teléfono debe tener una longitud válida (9 a 15 dígitos).")
        return telefono

#------------Producto----------------
class RegistroProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'categoria',
            'laboratorio',
            'unidad_medida',
            'temperatura',
            'precio_compra',
            'precio_venta',
            'iva',
            'estado'
        ]
    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']

        if Producto.objects.filter(codigo=codigo).exists():
            raise forms.ValidationError("Ya existe un producto con este código.")

        return codigo    
    
    def clean_precio_compra(self):
        precio = self.cleaned_data['precio_compra']

        if precio <= 0:
            raise forms.ValidationError("El precio de compra debe ser mayor a 0.")

        return precio
    
    def clean_precio_venta(self):
        precio = self.cleaned_data['precio_venta']

        if precio <= 0:
            raise forms.ValidationError("El precio de venta debe ser mayor a 0.")

        return precio
    
    def clean(self):
        cleaned_data = super().clean()

        compra = cleaned_data.get('precio_compra')
        venta = cleaned_data.get('precio_venta')

        if compra and venta:
            if venta < compra:
                raise forms.ValidationError(
                    "El precio de venta no puede ser menor al precio de compra."
                )

        return cleaned_data


class EditarProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # He incluido todos los campos de tu modelo
        fields = [
            'codigo', 'nombre', 'descripcion', 'categoria', 
            'laboratorio', 'unidad_medida', 'temperatura', 
            'precio_compra', 'precio_venta', 'iva', 'estado'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'laboratorio': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'temperatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'codigo': 'Código del Producto',
            'temperatura': 'Temperatura (°C)',
            'precio_compra': 'Precio de Compra',
            'precio_venta': 'Precio de Venta',
            'iva': 'IVA (%)',
        }

    def clean_precio_compra(self):
        precio = self.cleaned_data['precio_compra']
        if precio <= 0:
            raise forms.ValidationError("El precio de compra debe ser mayor a 0.")
        return precio

    def clean_precio_venta(self):
        precio = self.cleaned_data['precio_venta']
        if precio <= 0:
            raise forms.ValidationError("El precio de venta debe ser mayor a 0.")
        return precio

    def clean(self):
        cleaned_data = super().clean()
        compra = cleaned_data.get('precio_compra')
        venta = cleaned_data.get('precio_venta')
        if compra and venta:
            if venta < compra:
                raise forms.ValidationError(
                    "El precio de venta no puede ser menor al precio de compra."
                )
        return cleaned_data
#+----------------------------PROVEEDOR-----------------------------------------------

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        # Se añaden 'contacto' y 'estado' para coincidir con el modelo
        fields = [
            'ruc', 
            'nombre_empresa', 
            'contacto', 
            'telefono', 
            'correo', 
            'direccion', 
            'estado'
        ]
        widgets = {
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1712345678001'}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la persona de contacto'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0987654321'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@empresa.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    # Esta función se ejecuta automáticamente para validar el campo 'ruc'
    def clean_ruc(self):
        ruc = self.cleaned_data.get('ruc')
        
        # Validar que solo contenga números
        if not ruc.isdigit():
            raise forms.ValidationError("El RUC debe contener únicamente números.")
            
        # Validar que tenga exactamente 13 dígitos
        if len(ruc) != 13:
            raise forms.ValidationError("El RUC debe tener exactamente 13 dígitos.")
            
        return ruc
    
#----------------------------Compra----------------------
class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        # Los campos coinciden exactamente con el modelo Compra
        fields = [
            'proveedor', 
            'fecha', 
            'numero_factura', 
            'observacion', 
        ]
        
        # Etiquetas personalizadas para que se vean mejor en el HTML (opcional pero recomendado)
        labels = {
            'proveedor': 'Proveedor',
            'fecha': 'Fecha de Compra',
            'numero_factura': 'Número de Factura',
            'observacion': 'Observaciones',
        }
        
        # Widgets con clases de Bootstrap para el diseño
        widgets = {
            'proveedor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date' # Activa el calendario nativo del navegador
            }),
            'numero_factura': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 001-001-000012345'
            }),
            'observacion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, # Cambiado a 3 para dar un poco más de espacio
                'placeholder': 'Detalles adicionales de la entrega...'
            }),
        }
#-----------------------------Venta----------------------
class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = [
            'cliente',
            'fecha',
            'numero_factura',
            'observacion',
        ]

        labels = {
            'cliente': 'Cliente',
            'fecha': 'Fecha de Venta',
            'numero_factura': 'Número de Factura',
            'observacion': 'Observaciones',
        }

        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numero_factura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 001-001-000012345'
            }),
            'observacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detalles adicionales de la venta...'
            }),
        }
#-----------------------------RegistroDetalleCompra----------------------
class RegistroDetalleCompraForm(forms.ModelForm):

    class Meta:
        model = DetalleCompra
        fields = [
            'compra',
            'producto',
            'cantidad',
            'precio_unitario'
        ]

#-----------------------------Lote----------------------
class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = [
            'numero_lote',
            'fecha_fabricacion',
            'fecha_caducidad',
            'cantidad_recibida',
            'ubicacion',
            'estado',
        ]
        labels = {
            'numero_lote': 'Número de Lote',
            'fecha_fabricacion': 'Fecha de Fabricación',
            'fecha_caducidad': 'Fecha de Caducidad',
            'cantidad_recibida': 'Cantidad Recibida',
            'ubicacion': 'Ubicación',
            'estado': 'Estado',
        }
        widgets = {
            'numero_lote': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: LOTE-001',
            }),
            'fecha_fabricacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fecha_caducidad': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'cantidad_recibida': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
            'ubicacion': forms.Select(attrs={
                'class': 'form-select',
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def clean_fecha_caducidad(self):
        fecha_caducidad = self.cleaned_data.get('fecha_caducidad')
        fecha_fabricacion = self.cleaned_data.get('fecha_fabricacion')

        if fecha_fabricacion and fecha_caducidad:
            if fecha_caducidad <= fecha_fabricacion:
                raise forms.ValidationError(
                    "La fecha de caducidad debe ser posterior a la fecha de fabricación."
                )
        return fecha_caducidad

    def clean_cantidad_recibida(self):
        cantidad = self.cleaned_data.get('cantidad_recibida')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad


#-----------------------------Ubicacion----------------------
class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['planta', 'pasillo', 'estanteria', 'nivel', 'codigo']
        labels = {
            'planta': 'Planta',
            'pasillo': 'Pasillo',
            'estanteria': 'Estantería',
            'nivel': 'Nivel',
            'codigo': 'Código',
        }
        widgets = {
            'planta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Planta 1',
            }),
            'pasillo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pasillo A',
            }),
            'estanteria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Estantería 3',
            }),
            'nivel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Nivel 2',
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PL1-PA-E3-N2',
            }),
        }