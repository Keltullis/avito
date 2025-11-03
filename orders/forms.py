from django import forms
from .models import Order


class OrderForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 focus:border-black focus:outline-none input-checkout',
            'placeholder': 'Имя'
        }),
        label='Имя'
    )
    
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 focus:border-black focus:outline-none input-checkout',
            'placeholder': 'Фамилия'
        }),
        label='Фамилия'
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 focus:border-black focus:outline-none input-checkout',
            'placeholder': '+7 (___) ___-__-__'
        }),
        label='Номер телефона'
    )
    
    delivery_address = forms.ChoiceField(
        choices=Order.DELIVERY_ADDRESS_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 focus:border-black focus:outline-none select-checkout',
        }),
        label='Адрес получения'
    )
    
    group_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 focus:border-black focus:outline-none input-checkout',
            'placeholder': 'Например: И-207'
        }),
        label='Номер группы'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
