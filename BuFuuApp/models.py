from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    estrellas = models.PositiveIntegerField(default=0)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos"
    )

    def save(self, *args, **kwargs):
        if self.estrellas < 0:
            self.estrellas = 0
        elif self.estrellas > 5:
            self.estrellas = 5
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Carrito(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ItemCarrito')

    def __str__(self):
        return f"Carrito de {self.user.username}"


class ItemCarrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    ROLE_CHOICES = (
        ("cliente", "Cliente"),
        ("staff", "Staff"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="cliente")

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Pago(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
        ('in_process', 'En Proceso'),
    ]

    METODO_CHOICES = [
        ('mercadopago', 'Mercado Pago'),
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    orden_id = models.CharField(max_length=50, unique=True)
    monto = models.PositiveIntegerField()
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES, default='mercadopago')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pending')

    payment_id = models.CharField(max_length=100, blank=True, null=True)
    preference_id = models.CharField(max_length=100, blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    email_comprador = models.EmailField(blank=True, null=True)
    telefono_comprador = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Pago {self.orden_id} - {self.get_estado_display()}"

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'


class Orden(models.Model):
    ESTADO_CHOICES = [
        ('pendiente_revision', 'Pendiente de Revisión'),
        ('aprobada', 'Aprobada'),
        ('pagado', 'Pagado'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    orden_id = models.CharField(max_length=50, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.PositiveIntegerField()
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='pendiente_revision')

    pago = models.OneToOneField('Pago', on_delete=models.SET_NULL, null=True, blank=True)

    direccion_envio = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    aprobada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes_aprobadas')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Orden {self.orden_id} - {self.user.username}"

    class Meta:
        ordering = ['-fecha']


class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.PositiveIntegerField()
    notas_admin = models.TextField(blank=True, null=True)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
