
from django.shortcuts import render
from django.views import View
from django.db.models import OuterRef, Subquery, F, ExpressionWrapper, DecimalField, Case, When
from django.utils import timezone
from .models import Product, Discount, Cart, WishList
from rest_framework import viewsets, response
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer
from django.shortcuts import get_object_or_404, redirect
# from django.contrib.auth.models import User
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
from rest_framework import viewsets
from rest_framework import response
from rest_framework.generics import get_object_or_404
from .models import WishList
from .serializers import WishListSerializer
from rest_framework.permissions import IsAuthenticated


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart_items = self.get_queryset().filter(product__id=request.data.get('product'))
        if cart_items:
            cart_item = cart_items[0]
            if request.data.get('quantity'):
                cart_item.quantity += int(request.data.get('quantity'))
            else:
                cart_item.quantity += 1
        else:
            product = get_object_or_404(Product, id=request.data.get('product'))
            if request.data.get('quantity'):
                cart_item = Cart(user=request.user, product=product, quantity=request.data.get('quantity'))
            else:
                cart_item = Cart(user=request.user, product=product)
        cart_item.save()
        return response.Response({'message': 'Product added to cart'}, status=201)

    def update(self, request, *args, **kwargs):
        cart_item = get_object_or_404(Cart, id=kwargs['pk'])
        if request.data.get('quantity'):
            cart_item.quantity = request.data['quantity']
        if request.data.get('product'):
            product = get_object_or_404(Product, id=request.data['product'])
            cart_item.product = product
        cart_item.save()
        return response.Response({'message': 'Product change to cart'}, status=201)

    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_queryset().get(id=kwargs['pk'])
        cart_item.delete()
        return response.Response({'message': 'Product delete from cart'}, status=201)


class ShopView(View):

    def get(self, request):
        discount_value = Case(When(discount__value__gte=0,
                                   discount__date_begin__lte=timezone.now(),
                                   discount__date_end__gte=timezone.now(),
                                   then=F('discount__value')),
                              default=0,
                              output_field=DecimalField(max_digits=10, decimal_places=2)
                              )
        price_with_discount = ExpressionWrapper(
            F('price') * (100.0 - F('discount_value')) / 100.0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )

        products = Product.objects.annotate(
            discount_value=discount_value,
            price_before=F('price'),
            price_after=price_with_discount
        ).values('id', 'name', 'image', 'price_before', 'price_after',
                 'discount_value')
        return render(request, 'store/shop.html', {"data": products})


class CartView(View):

    def get(self, request):
        return render(request, "store/cart.html")


class ProductSingleView(View):

    def get(self, request, id):

        data = Product.objects.get(id=id)
        return render(request,
                      "store/product-single.html",
                      context={'name': data.name,
                               'description': data.description,
                               'price': data.price,
                               'rating': 5.0,
                               'url': data.image.url,
                               })


class WishListView(View):
    def get(self, request):
        if request.user.is_authenticated:
            wishlist = WishList.objects.filter(user=request.user)
            return render(request, "store/wishlist.html", {'wishlist': wishlist})
        return redirect('login:login')

class WishListRemoveView(View):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        wishlist_item = WishList.objects.filter(user=request.user, product=product)
        wishlist_item.delete()
        return redirect('store:wishlist')

class WishListAddView(View):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        wishlist_item = WishList.objects.filter(user=request.user, product=product)

        if wishlist_item.exists():
            return redirect('store:shop')
        else:
            wishlist_item = WishList(user=request.user, product=product)
            wishlist_item.save()
            return redirect('store:shop')
#
# class WishListView(APIView):
#     def get(self, request):
#         wishlist = WishList.objects.filter(user=request.user)
#         serializer = WishListSerializer(wishlist, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = WishListSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def put(self, request, pk):
#         wishlist_item = get_object_or_404(WishList, id=id, user=request.user)
#         serializer = WishListSerializer(wishlist_item, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         wishlist_item = get_object_or_404(WishList, id=id, user=request.user)
#         wishlist_item.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        wishlist_items = self.get_queryset().filter(product__id=request.data.get('product'))

        if wishlist_items:
            wishlist_item = wishlist_items[0]
        else:
            product = get_object_or_404(Product, id=request.data.get('product'))
            wishlist_item = WishList(user=request.user, product=product)

        wishlist_item.save()
        return response.Response({'message': 'Product added to wishlist'}, status=201)

    def update(self, request, *args, **kwargs):
        wishlist_item = get_object_or_404(WishList, id=kwargs['pk'])

        if request.data.get('product'):
            product = get_object_or_404(Product, id=request.data['product'])
            wishlist_item.product = product

        wishlist_item.save()
        return response.Response({'message': 'Product changed in wishlist'}, status=201)

    def destroy(self, request, *args, **kwargs):
        wishlist_item = self.get_queryset().get(id=kwargs['pk'])
        wishlist_item.delete()
        return response.Response({'message': 'Product deleted from wishlist'}, status=201)

