from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Wishlist


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'country', 'is_moderator', 'is_staff')
    list_filter = ('country', 'is_moderator', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'company',
                     'city', 'country')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'company', 'address1',
                       'address2', 'city', 'country', 'province', 'postal_code',
                       'phone')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_moderator',
                       'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1',
                       'password2', 'is_staff', 'is_active', 'is_moderator'),
        }),
    )


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            form.base_fields['username'].disabled = True

        return form


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__email', 'product__name')
    ordering = ('-added_at',)
    raw_id_fields = ('user', 'product')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Wishlist, WishlistAdmin)
