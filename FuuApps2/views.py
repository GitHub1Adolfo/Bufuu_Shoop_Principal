from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from BuFuuApp.models import Carrito, ItemCarrito, Orden, Pago
from datetime import datetime

@login_required
def boleta_view(request):
    """
    Muestra la boleta de la última orden pagada del usuario
    o de una orden específica si se pasa el ID
    """
    
    # Opción 1: Boleta de orden específica (desde link en pago exitoso)
    orden_id = request.GET.get('orden_id')
    
    if orden_id:
        try:
            orden = get_object_or_404(Orden, orden_id=orden_id, user=request.user)
            items = orden.items.all()
            total = orden.total
            pago = orden.pago
            
            # Preparar datos adicionales para cada item
            for item in items:
                item.total_producto = item.subtotal
            
            return render(request, 'modern_boleta.html', {
                'items': items,
                'total': total,
                'today': orden.fecha,
                'order_id': orden.orden_id,
                'pago': pago,
                'orden': orden,
            })
        except Orden.DoesNotExist:
            messages.error(request, 'Orden no encontrada')
            return redirect('menu')
    
    # Opción 2: Boleta de la última orden (comportamiento anterior)
    else:
        # Buscar la última orden pagada del usuario
        try:
            orden = Orden.objects.filter(
                user=request.user, 
                estado='pagado'
            ).order_by('-fecha').first()
            
            if not orden:
                # Si no hay orden pagada, mostrar carrito actual (compatibilidad con versión anterior)
                carrito = Carrito.objects.get(user=request.user)
                items = ItemCarrito.objects.filter(carrito=carrito)
                
                if not items.exists():
                    messages.warning(request, 'No tienes productos en el carrito')
                    return redirect('menu')
                
                total = 0 
                for item in items:
                    item.total_producto = item.producto.precio * item.cantidad
                    total += item.total_producto
                
                return render(request, 'modern_boleta.html', {
                    'items': items,
                    'total': total,
                    'today': datetime.now(),
                    'order_id': 'TEMP',
                })
            
            # Si hay orden, mostrar esa boleta
            items = orden.items.all()
            for item in items:
                item.total_producto = item.subtotal
                item.producto.nombre = item.producto.nombre  # Asegurar acceso
                item.producto.precio = item.precio_unitario  # Usar precio histórico
                item.cantidad = item.cantidad
            
            return render(request, 'modern_boleta.html', {
                'items': items,
                'total': orden.total,
                'today': orden.fecha,
                'order_id': orden.orden_id,
                'pago': orden.pago,
                'orden': orden,
            })
            
        except Exception as e:
            messages.error(request, 'Error al cargar la boleta')
            return redirect('menu')