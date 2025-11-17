from django.db import models
from django.utils.text import slugify
from django.conf import settings

try:
    from unidecode import unidecode
    HAS_UNIDECODE = True
except ImportError:
    HAS_UNIDECODE = False


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name
    

class Size(models.Model):
    name = models.CharField(max_length=20)


    def __str__(self):
        return self.name
    

class ProductSize(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                related_name='product_sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    custom_size = models.CharField(max_length=50, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)


    def __str__(self):
        size_name = self.custom_size if self.custom_size else (self.size.name if self.size else "Без размера")
        return f"{size_name} ({self.stock} in stock) for {self.product.name}"


class Product(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                              related_name='listings', null=True, blank=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    color = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to='products/main/')
    
    is_active = models.BooleanField(default=True)
    total_stock = models.PositiveIntegerField(default=0)
    no_size = models.BooleanField(default=False)
    
    condition = models.CharField(max_length=50, blank=True, 
                                 choices=[
                                     ('new', 'Новое'),
                                     ('like_new', 'Как новое'),
                                     ('good', 'Хорошее'),
                                     ('fair', 'Удовлетворительное')
                                 ])
    material = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            if HAS_UNIDECODE:
                transliterated_name = unidecode(self.name)
            else:
                transliterated_name = self.name
            
            base_slug = slugify(transliterated_name)
            
            if not base_slug:
                import uuid
                base_slug = f"product-{uuid.uuid4().hex[:8]}"
            
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        if self.total_stock == 0 and self.is_active:
            self.is_active = False
            
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name
    
    def is_available(self):
        return self.is_active and self.total_stock > 0
    
    def decrease_stock(self, quantity):
        """Уменьшить остаток товара и автоматически деактивировать если 0"""
        if self.total_stock >= quantity:
            self.total_stock -= quantity
            if self.total_stock == 0:
                self.is_active = False
            self.save()
            return True
        return False


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                                related_name='images')
    image = models.ImageField(upload_to='products/extra/')


class ContactMessage(models.Model):
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Email')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения от клиентов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Сообщение от {self.email} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='URL')
    image = models.ImageField(upload_to='blog/', verbose_name='Изображение')
    excerpt = models.TextField(max_length=300, verbose_name='Краткое описание')
    content = models.TextField(verbose_name='Полный текст статьи')
    author = models.CharField(max_length=100, default='Админ', verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    
    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи блога'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            if HAS_UNIDECODE:
                transliterated_title = unidecode(self.title)
            else:
                transliterated_title = self.title
            
            base_slug = slugify(transliterated_title)
            
            if not base_slug:
                import uuid
                base_slug = f"post-{uuid.uuid4().hex[:8]}"
            
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
