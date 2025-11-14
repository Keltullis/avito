from django.contrib import admin
from .models import Category, Size, Product, \
    ProductImage, ProductSize, ContactMessage, BlogPost


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'color']
    list_filter = ['category', 'color']
    search_fields = ['name', 'color', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSizeInline]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['email', 'phone', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('phone', 'email')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Статус', {
            'fields': ('is_read', 'created_at')
        }),
    )


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'is_published']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'author', 'image')
        }),
        ('Контент', {
            'fields': ('excerpt', 'content')
        }),
        ('Публикация', {
            'fields': ('is_published',)
        }),
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
