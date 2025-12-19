from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Producto  # Asegúrate de que 'Producto' esté correctamente importado desde el modelo

# Formulario de registro de usuario
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Correo Electrónico')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de Usuario'
        }

# Formulario personalizado de creación de usuario
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

# Formulario para agregar o editar productos (lo que faltaba agregar)
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'imagen', 'estrellas']  # Los campos que el admin puede modificar
        labels = {
            'nombre': 'Nombre del Producto',
            'precio': 'Precio',
            'estrellas': 'Calificación (de 0 a 5)',
        }


# forms.py
from django import forms
from .models import Categoria, Producto

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Ej: Bong, Grinders, Papelillos"
            })
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "precio", "imagen", "estrellas", "categoria"]


# ============================================
# NUEVO: Formulario de registro de administradores
# ============================================
class AdminRegisterForm(UserCreationForm):
    """
    Formulario para crear cuentas de administrador
    Incluye campos adicionales para permisos
    """
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'admin@bufuu.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre del administrador'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Apellido del administrador'
        })
    )
    
    is_superuser = forms.BooleanField(
        required=False,
        label='Superusuario',
        help_text='Otorga todos los permisos sin asignarlos explícitamente.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_superuser']
        labels = {
            'username': 'Nombre de Usuario'
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Elige un nombre de usuario'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirma la contraseña'
        })


# ============================================
# SISTEMA DE ROLES
# ============================================

# Opciones de roles
ROLE_CHOICES = [
    ('staff', 'Staff (Solo acceso básico)'),
    ('admin', 'Admin (Puede crear staff)'),
]

class CreateStaffForm(UserCreationForm):
    """
    Formulario para crear cuentas de Staff
    Usado por Admins y Superusers
    """
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'staff@bufuu.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Apellido'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'username': 'Nombre de Usuario'
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre de usuario'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirma la contraseña'
        })


class CreateAdminForm(UserCreationForm):
    """
    Formulario para crear cuentas de Admin
    Solo usado por Superusers
    """
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'admin@bufuu.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Apellido'
        })
    )
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Rol',
        widget=forms.RadioSelect(attrs={
            'class': 'role-radio'
        }),
        initial='staff'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role']
        labels = {
            'username': 'Nombre de Usuario'
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre de usuario'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirma la contraseña'
        })