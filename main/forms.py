from django import forms
from .models import Product, ProductImage, ProductSize, Size, ContactMessage


class ProductForm(forms.ModelForm):
    sizes = forms.ModelMultipleChoiceField(
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Размеры (если применимо)'
    )
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'color', 'description', 'main_image', 
                  'total_stock', 'condition', 'material', 'brand']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900',
                'placeholder': 'Название товара'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900'
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900',
                'placeholder': 'Цвет'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900',
                'rows': 4,
                'placeholder': 'Описание товара'
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900'
            }),
            'total_stock': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900',
                'min': '1',
                'placeholder': 'Количество'
            }),
            'condition': forms.Select(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900'
            }),
            'material': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900',
                'placeholder': 'Материал (необязательно)'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900',
                'placeholder': 'Бренд (необязательно)'
            }),
        }
        labels = {
            'name': 'Название',
            'category': 'Категория',
            'color': 'Цвет',
            'description': 'Описание',
            'main_image': 'Главное фото',
            'total_stock': 'Количество',
            'condition': 'Состояние',
            'material': 'Материал',
            'brand': 'Бренд',
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['phone', 'email', 'message']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 py-3 px-4 text-sm focus:outline-none focus:border-gray-900',
                'placeholder': '+7 (___) ___-__-__'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 py-3 px-4 text-sm focus:outline-none focus:border-gray-900',
                'placeholder': 'your@email.com'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 py-3 px-4 text-sm focus:outline-none focus:border-gray-900',
                'rows': 6,
                'placeholder': 'Ваш вопрос...'
            }),
        }
        labels = {
            'phone': 'Номер телефона',
            'email': 'Email',
            'message': 'Ваш вопрос',
        }
