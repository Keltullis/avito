from django.contrib import admin
from .models import ProductModeration


@admin.register(ProductModeration)
class ProductModerationAdmin(admin.ModelAdmin):
    list_display = ('product', 'status', 'moderator', 'created_at', 'moderated_at')
    list_filter = ('status', 'created_at', 'moderated_at')
    search_fields = ('product__name', 'moderator__email')
    raw_id_fields = ('product', 'moderator')
    readonly_fields = ('created_at',)
