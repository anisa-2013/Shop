from django.db import transaction
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, UpdateCartItemSerializer

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.prefetch_related('items__product').get(pk=cart.pk)

class AddCartItemView(generics.GenericAPIView):
    serializer_class = AddCartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            if item.quantity > product.stock:
                raise serializers.ValidationError({'quantity': 'Not enough stock.'})
            item.save(update_fields=['quantity'])
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class CartItemView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateCartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related('product')

    def patch(self, request, pk):
        with transaction.atomic():
            item = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            quantity = serializer.validated_data['quantity']
            if quantity > item.product.stock:
                raise serializers.ValidationError({'quantity': 'Not enough stock.'})
            item.quantity = quantity
            item.save(update_fields=['quantity'])
            return Response(CartItemSerializer(item).data)

    def delete(self, request, pk):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
