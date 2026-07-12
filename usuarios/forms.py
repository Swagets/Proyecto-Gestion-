from django import forms
from .models import Usuario

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'rol']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
            # Agrega más clases de Bootstrap a los otros campos aquí
        }