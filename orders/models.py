from django.db import models
from django.conf import settings
from main.models import Product, ProductSize
import random
import string


def generate_order_code():
    """Generate a unique 12-digit order code"""
    while True:
        code = ''.join(random.choices(string.digits, k=12))
        # Check if code already exists
        from orders.models import Order
        if not Order.objects.filter(order_code=code).exists():
            return code


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('processing', 'Обрабатывается'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )
    
    DELIVERY_ADDRESS_CHOICES = (
        ('address_1', 'Россия, Челябинск, Комсомольский проспект 113-а'),
        ('address_2', 'Россия, Челябинск, Кожзаводская улица, 1'),
        ('address_3', 'Россия, Челябинск, улица Комаровского, 9А'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='orders')
    order_code = models.CharField(max_length=12, unique=True, editable=False, blank=True, default='')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True, default='')
    phone = models.CharField(max_length=15)
    delivery_address = models.CharField(max_length=20, choices=DELIVERY_ADDRESS_CHOICES, blank=True)
    group_number = models.CharField(max_length=20, verbose_name='Номер группы', blank=True, default='')
    
    email = models.EmailField(max_length=254, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    address1 = models.CharField(max_length=100, blank=True, null=True)
    address2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    special_instructions = models.TextField(blank=True)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_provider = models.CharField(max_length=20, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    heleket_payment_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.order_code} - {self.first_name} {self.patronymic} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = generate_order_code()
        super().save(*args, **kwargs)
    
    def get_delivery_address_display_full(self):
        """Get full delivery address text"""
        return dict(self.DELIVERY_ADDRESS_CHOICES).get(self.delivery_address, '')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size.size.name} ({self.quantity})"
    
    def get_total_price(self):
        return self.price * self.quantity
