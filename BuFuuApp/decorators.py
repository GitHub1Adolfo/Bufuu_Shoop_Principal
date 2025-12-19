from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def staff_required(view_func):
    """Decorador para permitir solo a staff/admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('login')
        
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, '⛔ No tienes permisos de administrador')
            return redirect('inicio')
        
        return view_func(request, *args, **kwargs)
    return wrapper