from multiprocessing import context
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from .decorators import staff_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from .models import Orden, ItemOrden, Producto, Pago
from datetime import datetime
from django.db.models import Sum
from django.contrib import messages
from .models import UserProfile
import random
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User



from rest_framework.viewsets import ModelViewSet

from .models import Carrito, Producto, ItemCarrito, Categoria, Producto,Orden, Pago, ItemOrden
from .forms import UserRegisterForm, ProductoForm, CategoriaForm
from .serializers import ProductoSerializer, CarritoSerializer, ItemCarritoSerializer


def inicio(request):
    """
    Vista de página de inicio - usando template moderno
    """
    return render(request, 'modern_inicio.html')

def quienes_somos(request):
    return render(request, 'quienes_somos.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "¡Usuario creado con éxito!")
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/modern_register.html', {'form': form})


@require_POST
@login_required
# NO DEBE TENER: @csrf_exempt
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, created = Carrito.objects.get_or_create(user=request.user)
    item_carrito, created = ItemCarrito.objects.get_or_create(
        carrito=carrito, 
        producto=producto
    )

    if not created:
        item_carrito.cantidad += 1
        item_carrito.save()

    messages.success(request, f'Agregaste {producto.nombre} al carrito.')
    return redirect('menu')


@login_required
def carrito_compras(request):
    carrito, created = Carrito.objects.get_or_create(user=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    
    total = 0
    for item in items:
        item.total = item.producto.precio * item.cantidad
        total += item.total

    return render(request, 'modern_cart.html', {
        'carrito': items, 
        'total': total
    })


@login_required
def eliminar_del_carrito(request, item_id):
    carrito = Carrito.objects.get(user=request.user)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito con éxito.')
    return redirect('carrito_compras')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido, {username}!')
            return redirect('inicio')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    
    return render(request, 'registration/modern_login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('inicio')


def menu(request):
    query = request.GET.get('q', '').strip()

    # Base: todos
    productos = Producto.objects.all()

    # Si hay búsqueda, filtra
    if query:
        productos = productos.filter(nombre__icontains=query).distinct()

    # Estrellas
    for p in productos:
        p.estrellas_lista = ['⭐'] * p.estrellas + ['☆'] * (5 - p.estrellas)

    return render(request, 'modern_menu.html', {
        'productos': productos,  # ✅ tu HTML depende de esto
        'query': query
    })





@staff_member_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado con éxito.")
            return redirect('menu')
    else:
        form = ProductoForm()

    return render(request, 'agregar_producto.html', {'form': form})


@login_required
@require_POST
def actualizar_cantidad(request, item_id):
    carrito = Carrito.objects.get(user=request.user)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)

    action = request.POST.get('action')

    if action == 'increase':
        item.cantidad += 1
    elif action == 'decrease' and item.cantidad > 1:
        item.cantidad -= 1

    item.save()
    messages.success(request, "Cantidad actualizada con éxito.")
    return redirect('carrito_compras')


def pagar(request):
    return render(request, 'pagar.html')


# ============================================
# VIEWSETS PARA LA API REST
# ============================================
class ProductoViewSet(ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


class ItemCarritoViewSet(ModelViewSet):
    queryset = ItemCarrito.objects.all()
    serializer_class = ItemCarritoSerializer


class CarritoViewSet(ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer


# ============================================
# VISTAS DE ADMINISTRACIÓN DE PRODUCTOS
# ============================================
@staff_member_required
def actualizar_estrellas(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'increase' and producto.estrellas < 5:
            producto.estrellas += 1
        elif action == 'decrease' and producto.estrellas > 0:
            producto.estrellas -= 1
        
        producto.save()
        messages.success(
            request, 
            f"Estrellas del producto {producto.nombre} actualizadas a {producto.estrellas}."
        )
    
    return redirect('menu')


@staff_member_required
def actualizar_nombre(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        
        if nombre:
            producto.nombre = nombre
            producto.save()
            messages.success(
                request, 
                f"El nombre del producto ha sido actualizado a '{producto.nombre}'."
            )
    
    return redirect('menu')


@staff_member_required
def actualizar_precio(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        precio = request.POST.get('precio')
        
        if precio:
            try:
                producto.precio = int(precio)
                producto.save()
                messages.success(
                    request, 
                    f"El precio del producto '{producto.nombre}' ha sido actualizado."
                )
            except ValueError:
                messages.error(request, "El precio debe ser un número válido.")
    
    return redirect('menu')


@staff_member_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    nombre_producto = producto.nombre
    producto.delete()
    messages.success(request, f"El producto '{nombre_producto}' ha sido eliminado.")
    return redirect('menu')

def solo_staff(view):
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view)


@solo_staff
def categorias(request):
    q = request.GET.get("q", "").strip()
    categorias = Categoria.objects.all()

    if q:
        categorias = categorias.filter(nombre__icontains=q)

    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada correctamente.")
            return redirect("categorias")
    else:
        form = CategoriaForm()

    return render(request, "categorias.html", {
        "form": form,
        "categorias": categorias,
        "q": q
    })


@solo_staff
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == "POST":
        categoria.delete()
        messages.success(request, "Categoría eliminada.")
    return redirect("categorias")


def menu(request):
    query = request.GET.get("q", "").strip()

    productos = Producto.objects.select_related("categoria").all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(categoria__nombre__icontains=query)
        ).distinct()

    return render(request, "modern_menu.html", {
        "productos": productos,
        "query": query
    })

@login_required
def checkout(request):
    """Página de checkout con resumen de compra"""
    carrito = Carrito.objects.get(user=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    
    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('menu')
    
    total = sum(item.producto.precio * item.cantidad for item in items)
    
    # Calcular envío (puedes hacerlo más sofisticado)
    envio = 0 if total > 30000 else 3000
    total_final = total + envio
    
    # Para cada item, calcular total
    for item in items:
        item.total = item.producto.precio * item.cantidad
    
    return render(request, 'modern_checkout.html', {
        'items': items,
        'subtotal': total,
        'envio': envio,
        'total': total_final,
    })


@login_required
def checkout(request):
    """Página de checkout"""
    try:
        carrito = Carrito.objects.get(user=request.user)
        items = ItemCarrito.objects.filter(carrito=carrito)
        
        if not items.exists():
            messages.warning(request, 'Tu carrito está vacío')
            return redirect('menu')
        
        # Calcular totales
        total = sum(item.producto.precio * item.cantidad for item in items)
        envio = 0 if total > 30000 else 3000
        total_final = total + envio
        
        # Agregar totales a items
        for item in items:
            item.total = item.producto.precio * item.cantidad
        
        return render(request, 'modern_checkout.html', {
            'items': items,
            'subtotal': total,
            'envio': envio,
            'total': total_final,
        })
    except Carrito.DoesNotExist:
        messages.error(request, 'Carrito no encontrado')
        return redirect('menu')


# ============================================
# CREAR PAGO (PROCESAR CHECKOUT)
# ============================================

@login_required
def crear_preferencia_pago(request):
    """Procesar el checkout y crear la orden"""
    if request.method != 'POST':
        return redirect('checkout')
    
    try:
        carrito = Carrito.objects.get(user=request.user)
        items = ItemCarrito.objects.filter(carrito=carrito)
        
        if not items.exists():
            messages.error(request, 'Tu carrito está vacío')
            return redirect('menu')
        
        # Calcular totales
        total = sum(item.producto.precio * item.cantidad for item in items)
        envio = 0 if total > 30000 else 3000
        total_final = total + envio
        
        # Generar orden_id único
        orden_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"
        
        # Capturar datos del formulario
        direccion = request.POST.get('direccion', '')
        ciudad = request.POST.get('ciudad', '')
        region = request.POST.get('region', '')
        notas = request.POST.get('notas', '')
        telefono = request.POST.get('telefono', '')
        metodo_pago = request.POST.get('payment_method', 'efectivo')
        
        print(f"📦 Creando orden: {orden_id}")
        print(f"💳 Método de pago: {metodo_pago}")
        
        # ⚠️ IMPORTANTE: Estado depende del método de pago
        if metodo_pago == 'efectivo':
            estado_orden = 'pendiente_revision'  # Necesita revisión del staff
            estado_pago = 'pending'
        else:
            estado_orden = 'pagado'  # Otros métodos se aprueban automáticamente
            estado_pago = 'approved'
        
        # Crear orden
        orden = Orden.objects.create(
            user=request.user,
            orden_id=orden_id,
            total=total_final,
            estado=estado_orden,  # ⚠️ Estado dinámico
            direccion_envio=direccion,
            ciudad=ciudad,
            region=region,
            notas=notas,
        )
        
        print(f"✅ Orden creada con estado: {estado_orden}")
        
        # Crear items de la orden
        for item in items:
            ItemOrden.objects.create(
                orden=orden,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
        
        # Crear pago
        pago = Pago.objects.create(
            user=request.user,
            orden_id=orden_id,
            monto=total_final,
            metodo_pago=metodo_pago,
            estado=estado_pago,  # ⚠️ Estado dinámico
            email_comprador=request.user.email,
            telefono_comprador=telefono,
        )
        
        print(f"💳 Pago creado con estado: {estado_pago}")
        
        # Asociar pago con orden
        orden.pago = pago
        orden.save()
        
        # Limpiar carrito
        items.delete()
        
        # Mensaje según método de pago
        if metodo_pago == 'efectivo':
            messages.success(request, '¡Orden creada! Tu pedido está en revisión.')
        else:
            messages.success(request, '¡Pago procesado exitosamente!')
        
        # Redirigir a página de éxito
        return HttpResponseRedirect(f'/pago/exitoso/?orden_id={orden_id}')
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error: {str(e)}')
        return redirect('checkout')


# ============================================
# PAGO EXITOSO
# ============================================

@login_required
def pago_exitoso(request):
    """Página de pago exitoso - muestra QR si es efectivo"""
    orden_id = request.GET.get('orden_id')
    
    if not orden_id:
        messages.warning(request, 'No se encontró la orden')
        return redirect('menu')
    
    try:
        orden = Orden.objects.get(orden_id=orden_id, user=request.user)
        pago = orden.pago
        
        # Generar QR para la orden
        from .utils import generar_qr_orden
        
        # QR para que el ADMIN edite la orden
        qr_admin = generar_qr_orden(request, orden_id, tipo='admin')
        
        # QR para que el CLIENTE vea su estado
        qr_cliente = generar_qr_orden(request, orden_id, tipo='cliente')
        
        # Si el pago es en efectivo y está pendiente de revisión
        if pago.metodo_pago == 'efectivo' and orden.estado == 'pendiente_revision':
            return render(request, 'modern_pago_pendiente.html', {
                'orden': orden,
                'pago': pago,
                'qr_cliente': qr_cliente,  # QR para que cliente vea estado
                'qr_admin': qr_admin,      # QR para que admin edite
            })
        
        # Si ya está aprobada o es otro método de pago
        return render(request, 'modern_pago_exitoso.html', {
            'orden': orden,
            'pago': pago,
        })
        
    except Orden.DoesNotExist:
        messages.error(request, 'Orden no encontrada')
        return redirect('menu')


# ============================================
# PAGO FALLIDO
# ============================================

@login_required
def pago_fallido(request):
    """Página de pago fallido"""
    return render(request, 'modern_pago_fallido.html')


# ============================================
# PAGO PENDIENTE
# ============================================

@login_required
def pago_pendiente(request):
    """Página de pago pendiente"""
    orden_id = request.GET.get('orden_id')
    orden = None
    
    if orden_id:
        try:
            orden = Orden.objects.get(orden_id=orden_id, user=request.user)
        except Orden.DoesNotExist:
            pass
    
    return render(request, 'modern_pago_pendiente.html', {
        'orden': orden,
    })


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def webhook_mercadopago(request):
    """Webhook de Mercado Pago (placeholder)"""
    return HttpResponse(status=200)


from django.conf import settings
from django.contrib.auth import views as auth_views
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import os


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/modern_password_reset.html'
    html_email_template_name = 'registration/password_reset_email.html'
    email_template_name = 'registration/password_reset_email.txt'  # opcional (texto)
    subject_template_name = 'registration/password_reset_subject.txt'  # opcional

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None
    ):
        # Asunto
        subject = render_to_string(subject_template_name, context).strip()

        # HTML del correo
        html_content = render_to_string(html_email_template_name, context)

        # Texto plano (fallback)
        text_content = render_to_string(email_template_name, context) if email_template_name else ""

        # Crear email multi-parte
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach_alternative(html_content, "text/html")

        # Adjuntar imagen embebida (CID)
        logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_gmail.png")

        print("LOGO PATH:", logo_path)
        print("EXISTS:", os.path.exists(logo_path))

        with open(logo_path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", "<bufuu_logo>")
            img.add_header("Content-Disposition", "inline", filename="logo_gmail.png")
            email.attach(img)
            email.send()

@staff_required
def editar_orden(request, orden_id):
    """
    Vista para que admin/staff edite una orden antes de aprobarla
    """
    orden = get_object_or_404(Orden, orden_id=orden_id)
    items = orden.items.all()
    
    # Solo se puede editar si está pendiente de revisión
    if orden.estado not in ['pendiente_revision', 'pendiente']:
        messages.warning(request, 'Esta orden ya fue procesada')
        return redirect('lista_ordenes_admin')
    
    # Recalcular total
    total_calculado = sum(item.subtotal for item in items)
    
    return render(request, 'admin_editar_orden.html', {
        'orden': orden,
        'items': items,
        'total': total_calculado,
        'productos_disponibles': Producto.objects.all(),
    })


@staff_required
def actualizar_item_orden(request, item_id):
    """
    API para actualizar un item de la orden (AJAX)
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        item = get_object_or_404(ItemOrden, id=item_id)
        
        # Actualizar campos
        item.cantidad = int(data.get('cantidad', item.cantidad))
        item.precio_unitario = int(data.get('precio', item.precio_unitario))
        item.notas_admin = data.get('notas', '')
        item.save()
        
        # Recalcular total de la orden
        orden = item.orden
        nuevo_total = sum(i.subtotal for i in orden.items.all())
        orden.total = nuevo_total
        orden.save()
        
        return JsonResponse({
            'success': True,
            'subtotal': item.subtotal,
            'total_orden': orden.total
        })
    
    return JsonResponse({'success': False}, status=400)


@staff_required
def eliminar_item_orden(request, item_id):
    """Eliminar un item de la orden"""
    if request.method == 'POST':
        item = get_object_or_404(ItemOrden, id=item_id)
        orden = item.orden
        
        item.delete()
        
        # Recalcular total
        nuevo_total = sum(i.subtotal for i in orden.items.all())
        orden.total = nuevo_total
        orden.save()
        
        messages.success(request, 'Producto eliminado')
        return redirect('editar_orden', orden_id=orden.orden_id)
    
    return redirect('lista_ordenes_admin')


@staff_required
def agregar_item_orden(request, orden_id):
    """Agregar un producto a la orden"""
    if request.method == 'POST':
        orden = get_object_or_404(Orden, orden_id=orden_id)
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        
        producto = get_object_or_404(Producto, id=producto_id)
        
        # Crear nuevo item
        ItemOrden.objects.create(
            orden=orden,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio
        )
        
        # Recalcular total
        nuevo_total = sum(i.subtotal for i in orden.items.all())
        orden.total = nuevo_total
        orden.save()
        
        messages.success(request, f'{producto.nombre} agregado a la orden')
        return redirect('editar_orden', orden_id=orden.orden_id)
    
    return redirect('lista_ordenes_admin')


@staff_required
def aprobar_orden(request, orden_id):
    """
    Aprobar la orden y generar boleta final
    """
    if request.method == 'POST':
        orden = get_object_or_404(Orden, orden_id=orden_id)
        
        # Cambiar estado
        orden.estado = 'aprobada'
        orden.aprobada_por = request.user
        orden.fecha_aprobacion = datetime.now()
        orden.save()
        
        # Actualizar pago
        if orden.pago:
            orden.pago.estado = 'approved'
            orden.pago.save()
        
        messages.success(request, f'✅ Orden {orden_id} aprobada exitosamente')
        return redirect('lista_ordenes_admin')
    
    return redirect('editar_orden', orden_id=orden_id)


# ============================================
# LISTA DE ÓRDENES PARA ADMIN
# ============================================

@staff_required
def lista_ordenes_admin(request):
    """
    Vista para que admin vea todas las órdenes pendientes y aprobadas
    """
    # Filtros
    estado_filter = request.GET.get('estado', 'todos')
    
    ordenes = Orden.objects.all().select_related('user', 'pago')
    
    if estado_filter != 'todos':
        ordenes = ordenes.filter(estado=estado_filter)
    
    # Estadísticas
    stats = {
        'pendientes': Orden.objects.filter(estado='pendiente_revision').count(),
        'aprobadas': Orden.objects.filter(estado='aprobada').count(),
        'total_ventas': Orden.objects.filter(estado__in=['aprobada', 'pagado']).aggregate(Sum('total'))['total__sum'] or 0,
    }
    
    return render(request, 'admin_ordenes.html', {
        'ordenes': ordenes,
        'stats': stats,
        'estado_filter': estado_filter,
    })


# ============================================
# VISTA QR PARA CLIENTE (VE ESTADO)
# ============================================

@login_required
def ver_qr_orden(request, orden_id):
    """
    Vista del QR del cliente
    - Si la orden está pendiente: muestra "En revisión"
    - Si está aprobada: muestra la boleta completa
    """
    orden = get_object_or_404(Orden, orden_id=orden_id, user=request.user)
    
    if orden.estado in ['pendiente_revision', 'pendiente']:
        # Mostrar página de espera
        return render(request, 'cliente_orden_pendiente.html', {
            'orden': orden,
        })
    
    elif orden.estado in ['aprobada', 'pagado', 'completado']:
        # Mostrar boleta completa
        items = orden.items.all()
        for item in items:
            item.total_producto = item.subtotal
        
        return render(request, 'modern_boleta.html', {
            'items': items,
            'total': orden.total,
            'today': orden.fecha,
            'order_id': orden.orden_id,
            'pago': orden.pago,
            'orden': orden,
        })
    
    else:
        # Cancelada u otro estado
        messages.warning(request, 'Esta orden no está disponible')
        return redirect('menu')


# ============================================
# HISTORIAL DE ÓRDENES DEL USUARIO
# ============================================

@login_required
def mis_ordenes(request):
    """
    Vista para que el usuario vea su historial de órdenes
    """
    ordenes = Orden.objects.filter(user=request.user).order_by('-fecha')
    
    return render(request, 'mis_ordenes.html', {
        'ordenes': ordenes,
    })

@login_required
def ver_qr_cliente(request, orden_id):
    orden = get_object_or_404(Orden, orden_id=orden_id, user=request.user)

    if orden.estado not in ['pendiente_revision', 'pendiente']:
        return redirect('ver_qr_orden', orden_id=orden_id)

    from .utils import generar_qr_orden

    return render(request, 'modern_pago_pendiente.html', {
        'orden': orden,
        'qr_cliente': generar_qr_orden(request, orden_id, 'cliente'),
        'qr_admin': generar_qr_orden(request, orden_id, 'admin'),
    })


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import UserRegisterForm, ProductoForm, AdminRegisterForm

@staff_member_required
def register_admin(request):
    """
    Vista para que solo admins puedan crear nuevas cuentas de administrador
    Requiere que el usuario actual sea staff
    """
    if request.method == 'POST':
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Establecer permisos de admin
            user.is_staff = True
            user.is_superuser = form.cleaned_data.get('is_superuser', False)
            user.save()
            
            messages.success(request, f'¡Cuenta de administrador creada exitosamente para {user.username}!')
            return redirect('menu')
    else:
        form = AdminRegisterForm()

    return render(request, 'registration/register_admin.html', {'form': form})

@staff_member_required
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

@staff_member_required
def create_user(request):
    return render(request, "admin_create_user.html")

@staff_member_required
def edit_user_role(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=user_obj)

    if request.method == "POST":
        new_role = request.POST.get("role", "cliente")
        profile.role = new_role
        profile.save()

        # opcional: sincroniza flags django
        if new_role in ("staff", "admin"):
            user_obj.is_staff = True
        else:
            user_obj.is_staff = False
            user_obj.is_superuser = False

        if new_role == "admin":
            user_obj.is_superuser = True

        user_obj.save()
        messages.success(request, f"Rol actualizado: {user_obj.username} → {new_role}")
        return redirect("admin_dashboard")  # cambia si tu dashboard tiene otro name

    return render(request, "admin_edit_user_role.html", {
        "user_obj": user_obj,
        "profile": profile,
        "roles": UserProfile.ROLE_CHOICES,
    })