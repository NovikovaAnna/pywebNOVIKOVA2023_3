from django.urls import path
from .views import ShopView, CartView, ProductSingleView, CartViewSet, WishListView, WishListRemoveView, WishListAddView, WishlistViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'cart', CartViewSet)
router.register(r'wishlist', WishlistViewSet)


app_name = 'store'

urlpatterns = [
    path('', ShopView.as_view(), name='shop'),
    path('cart/', CartView.as_view(), name='cart'),
    path('product/<int:id>/', ProductSingleView.as_view(), name='product'),
    path('wishlist', WishListView.as_view(), name='wishlist'),
    path('wishlist/remove/<int:id>/', WishListRemoveView.as_view(), name='remove_from_wishlist'),
    path('wishlist/add/<int:id>/', WishListAddView.as_view(), name='add_to_wishlist'),
    #path('api/', include(router.urls)),

]
