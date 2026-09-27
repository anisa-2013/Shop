from django.db import transaction
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from cart.models import Cart, CartItem
from catalog.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.select_for_update().get_or_create(user=request.user)
        cart_items = list(CartItem.objects.filter(cart=cart).select_related('product').order_by('product_id'))
        if not cart_items:
            raise serializers.ValidationError({'cart': 'Cart is empty.'})
        products = {p.pk: p for p in Product.objects.select_for_update().filter(pk__in=[item.product_id for item in cart_items]).order_by('pk')}
        for item in cart_items:
            if item.quantity > products[item.product_id].stock:
                raise serializers.ValidationError({'stock': f'Not enough stock for product {item.product_id}.'})
        order = Order.objects.create(user=request.user)
        OrderItem.objects.bulk_create([
            OrderItem(order=order, product_id=item.product_id, quantity=item.quantity,
                      price_at_order=products[item.product_id].price) for item in cart_items
        ])
        for item in cart_items:
            product = products[item.product_id]
            product.stock -= item.quantity
            product.save(update_fields=['stock'])
        CartItem.objects.filter(cart=cart).delete()
        order = Order.objects.prefetch_related('items__product').get(pk=order.pk)
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')
