from django.urls import path
from .views import AddCartItemView, CartItemView, CartView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/items/', AddCartItemView.as_view(), name='cart-item-add'),
    path('cart/items/<int:pk>/', CartItemView.as_view(), name='cart-item-detail'),
]
