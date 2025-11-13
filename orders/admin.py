from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('image_preview', 'product', 'size', 'quantity')
    readonly_fields = ('image_preview',)
    can_delete = False

    def image_preview(self, obj):
        if obj.product.main_image:
            return mark_safe(f'<img src="{obj.product.main_image.url}" style="max-height: 100px; max-width: 100px; object-fit: cover;" />')
        return mark_safe('<span style="color: gray;">Нет изображения</span>')
    image_preview.short_description = 'Изображение'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'user', 'full_name', 'group_number',
                    'status', 'created_at')
    list_filter = ('status', 'delivery_address', 'created_at')
    search_fields = ('order_code', 'first_name', 'last_name', 'patronymic', 'phone', 'group_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('order_code', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('order_code', 'user', 'status')
        }),
        ('Данные получателя', {
            'fields': ('first_name', 'last_name', 'patronymic', 'phone', 'group_number', 
                       'delivery_address')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'ФИО'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user', 'first_name', 'last_name', 'patronymic',
                                            'phone', 'group_number', 'delivery_address')
        return self.readonly_fields