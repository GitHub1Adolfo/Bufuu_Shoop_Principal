from rest_framework import serializers
from .models import Producto, Carrito, ItemCarrito

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ItemCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarrito
        fields = '__all__'

class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(source='itemcarrito_set', many=True, read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'user', 'items']
