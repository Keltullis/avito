from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        max_length=254, 
        widget=forms.EmailInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'РАБОЧАЯ ПОЧТА'
        })
    )
    first_name = forms.CharField(
        required=True, 
        max_length=50, 
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ИМЯ'
        })
    )
    last_name = forms.CharField(
        required=True, 
        max_length=50, 
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ФАМИЛИЯ'
        })
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ПАРОЛЬ'
        })
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ПОДТВЕРДИТЕ ПАРОЛЬ'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    ALLOWED_DOMAINS = ['inueco.ru', 'preco.ru', 'live.inueco.ru', 'live.preco.ru']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email domain is allowed
        if email:
            domain = email.split('@')[-1].lower()
            if domain not in self.ALLOWED_DOMAINS:
                raise forms.ValidationError('Регистрация доступна только по рабочей почте')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже используется')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = None
        if commit:
            user.save()
        return user


class EmailVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500 text-center text-2xl tracking-widest',
            'placeholder': '000000',
            'maxlength': '6',
            'autocomplete': 'off',
        }),
        label='Код подтверждения'
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise forms.ValidationError('Код должен содержать только цифры')
        return code
    

class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email", 
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ПОЧТА'
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ПАРОЛЬ'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Неверный email или пароль')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Этот аккаунт неактивен')
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    phone = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', "Введите корректный номер телефона")],
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'НОМЕР ТЕЛЕФОНА'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ИМЯ'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ФАМИЛИЯ'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
            'placeholder': 'ПОЧТА'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'company', 
                  'address1', 'address2', 'city', 'country',
                  'province', 'postal_code', 'phone')
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
                'placeholder': 'КОМПАНИЯ'
            }),
            'address1': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
                'placeholder': 'АДРЕС СТРОКА 1'
            }),
            'address2': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
                'placeholder': 'АДРЕС СТРОКА 2'
            }),
            'city': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
                'placeholder': 'ГОРОД'
            }),
            'country': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
                'placeholder': 'СТРАНА'
            }),
            'province': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
                'placeholder': 'РЕГИОН'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500', 
                'placeholder': 'ПОЧТОВЫЙ ИНДЕКС'
            }),
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Этот email уже используется')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('email'):
            cleaned_data['email'] = self.instance.email
        for field in ['company', 'address1', 'address2', 'city', 'country',
                      'province', 'postal_code', 'phone']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data
