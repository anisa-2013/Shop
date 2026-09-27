from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from cart.models import CartItem
from catalog.models import Category, Product
from .models import Order, OrderItem


class ShopFlowTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(username='buyer', password='StrongPass459!')
        self.other = User.objects.create_user(username='other', password='StrongPass459!')
        category = Category.objects.create(name='Books')
        self.product = Product.objects.create(
            name='Book', category=category, price=Decimal('12.50'), stock=5
        )
        self.client = APIClient()
        self.client.force_authenticate(self.buyer)

    def test_checkout_snapshots_price_reduces_stock_and_clears_cart(self):
        added = self.client.post('/api/cart/items/', {'product': self.product.pk, 'quantity': 2})
        self.assertEqual(added.status_code, 201)
        response = self.client.post('/api/orders/', {}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['total'], '25.00')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertFalse(CartItem.objects.filter(cart__user=self.buyer).exists())
        self.assertEqual(OrderItem.objects.get(order__user=self.buyer).price_at_order, Decimal('12.50'))
        self.assertEqual(self.client.post('/api/orders/', {}, format='json').status_code, 400)

    def test_users_cannot_read_other_orders_or_modify_products(self):
        order = Order.objects.create(user=self.other)
        self.assertEqual(self.client.get(f'/api/orders/{order.pk}/').status_code, 404)
        self.assertEqual(self.client.patch(f'/api/products/{self.product.pk}/', {'price': '1.00'}).status_code, 405)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get('/api/cart/').status_code, 401)
