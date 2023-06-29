from rest_framework import serializers
from .models import Cart, WishList

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class WishListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = WishList
        fields = '__all__'

# class WishListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WishList
#         fields = '__all__'