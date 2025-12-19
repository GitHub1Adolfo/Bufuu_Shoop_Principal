from django.contrib import admin
from django.urls import path, include
from BuFuuApp import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings
from BuFuuApp.views import agregar_al_carrito, register, actualizar_cantidad
from BuFuuApp.views import ProductoViewSet, CarritoViewSet, ItemCarritoViewSet
from rest_framework.routers import DefaultRouter
from BuFuuApp.views import CustomPasswordResetView

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'carritos', CarritoViewSet, basename='carrito')
router.register(r'items', ItemCarritoViewSet, basename='itemcarrito')

urlpatterns = [
    # Páginas principales
    path('', views.inicio, name='inicio'),
    path('menu/', views.menu, name='menu'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    
    # Carrito
    path('carrito/', views.carrito_compras, name='carrito_compras'),
    path('agregar_al_carrito/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', actualizar_cantidad, name='actualizar_cantidad'),
    path('eliminar_del_carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('pagar/', views.pagar, name='pagar'),
    
    # Autenticación - CORREGIDO para usar templates modernos
    path('register/', register, name='register'),
    path('accounts/login/', 
         auth_views.LoginView.as_view(template_name='registration/modern_login.html'),  # ← CAMBIO AQUÍ
         name='login'),
     path('accounts/logout/', 
         auth_views.LogoutView.as_view(), 
         name='logout'),
    
    # Password Reset - usando vista custom (HTML + CID)
     path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),

     path('password_reset/done/',
          auth_views.PasswordResetDoneView.as_view(
          template_name='registration/password_reset_done.html'
          ),
          name='password_reset_done'),

     path('reset/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(
          template_name='registration/password_reset_confirm.html'
          ),
          name='password_reset_confirm'),

     path('reset/done/',
          auth_views.PasswordResetCompleteView.as_view(
          template_name='registration/password_reset_complete.html'
          ),
          name='password_reset_complete'),

    
    # Boleta
    path('boleta/', include('FuuApps2.urls')),
    
    # API
    path('api/', include(router.urls)),
    
    # Admin
    path('admin/', admin.site.urls),
    path('register-admin/', views.register_admin, name='register_admin'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/create/', views.create_user, name='create_user'),
    path('admin/users/<int:user_id>/edit-role/', views.edit_user_role, name='edit_user_role'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),

    # Admin de categorías
    path("categorias/", views.categorias, name="categorias"),
    path("categorias/<int:categoria_id>/eliminar/", views.eliminar_categoria, name="eliminar_categoria"),

    # Admin de productos
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('actualizar_nombre/<int:producto_id>/', views.actualizar_nombre, name='actualizar_nombre'),
    path('actualizar_precio/<int:producto_id>/', views.actualizar_precio, name='actualizar_precio'),
    path('actualizar_estrellas/<int:producto_id>/', views.actualizar_estrellas, name='actualizar_estrellas'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('menu/<int:producto_id>/', views.menu, name='menu'),


    # Órdenes Cliente
    path('mis-ordenes/', views.mis_ordenes, name='mis_ordenes'),
    path('orden/<str:orden_id>/ver/', views.ver_qr_orden, name='ver_qr_orden'),
    path('orden/<str:orden_id>/qr/', views.ver_qr_cliente, name='ver_qr_cliente'),


    # ⚠️ GESTIÓN DE ÓRDENES (STAFF) - Usar "gestion" en lugar de "admin"
    path('gestion/ordenes/', views.lista_ordenes_admin, name='lista_ordenes_admin'),
    path('gestion/orden/<str:orden_id>/editar/', views.editar_orden, name='editar_orden'),
    path('gestion/orden/<str:orden_id>/aprobar/', views.aprobar_orden, name='aprobar_orden'),
    path('gestion/orden/item/<int:item_id>/actualizar/', views.actualizar_item_orden, name='actualizar_item_orden'),
    path('gestion/orden/item/<int:item_id>/eliminar/', views.eliminar_item_orden, name='eliminar_item_orden'),
    path('gestion/orden/<str:orden_id>/agregar-item/', views.agregar_item_orden, name='agregar_item_orden'),


    path('checkout/', views.checkout, name='checkout'),
    path('crear-pago/', views.crear_preferencia_pago, name='crear_pago'),
    path('pago/exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago/fallido/', views.pago_fallido, name='pago_fallido'),
    path('pago/pendiente/', views.pago_pendiente, name='pago_pendiente'),
    path('webhook/mercadopago/', views.webhook_mercadopago, name='webhook_mercadopago'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
