from django import forms
from .models import Usuario, Producto
from django.contrib.auth.password_validation import validate_password

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