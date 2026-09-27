from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f'Cart #{self.pk} ({self.user})'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=('cart', 'product'), name='unique_cart_product')]

    def __str__(self):
        return f'{self.quantity} × {self.product}'
