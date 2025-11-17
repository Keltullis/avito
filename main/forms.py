from django import forms
from .models import Product, ProductImage, ProductSize, Size, ContactMessage


class ProductForm(forms.ModelForm):
    sizes = forms.ModelMultipleChoiceField(
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Размеры (если применимо)'
    )
    custom_size = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:border-gray-900',
            'placeholder': 'Например: 44, M, 42-44',
            'id': 'custom_size_input',
            'style': 'display: none;'
        }),
        label='Укажите размер'
    )
    no_size = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'border border-gray-300',
            'id': 'no_size_checkbox'
        }),
        label='Нет размера'
    )
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'color', 'description', 'main_image', 
                  'total_stock', 'condition', 'material', 'brand', 'no_size']
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
                'placeholder': 'Цвет (необязательно)'
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
            'color': 'Цвет (необязательно)',
            'description': 'Описание',
            'main_image': 'Главное фото',
            'total_stock': 'Количество',
            'condition': 'Состояние',
            'material': 'Материал',
            'brand': 'Бренд',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].required = False


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
