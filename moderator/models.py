from django.db import models
from django.conf import settings
from main.models import Product


class ModerationStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидает модерации'
    APPROVED = 'approved', 'Одобрено'
    REJECTED = 'rejected', 'Отклонено'


class ProductModeration(models.Model):
    """Модель для отслеживания статуса модерации объявлений"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='moderation')
    status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Модерация объявления'
        verbose_name_plural = 'Модерация объявлений'

    def __str__(self):
        return f"{self.product.name} - {self.get_status_display()}"
