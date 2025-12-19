from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'imagen', 'estrellas')
    search_fields = ('nombre',)
    actions = ['aumentar_estrellas', 'disminuir_estrellas']

    def aumentar_estrellas(self, request, queryset):
        for producto in queryset:
            if producto.estrellas < 5:
                producto.estrellas += 1
                producto.save()
        self.message_user(request, "Estrellas aumentadas en 1 para los productos seleccionados.")

    def disminuir_estrellas(self, request, queryset):
        for producto in queryset:
            if producto.estrellas > 0:
                producto.estrellas -= 1
                producto.save()
        self.message_user(request, "Estrellas disminuidas en 1 para los productos seleccionados.")

    aumentar_estrellas.short_description = "Aumentar estrellas"
    disminuir_estrellas.short_description = "Disminuir estrellas"
