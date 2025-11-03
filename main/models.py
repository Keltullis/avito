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
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.size.name} ({self.stock} in stock) for {self.product.name}"


class Product(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                              related_name='listings', null=True, blank=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    color = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to='products/main/')
    
    is_active = models.BooleanField(default=True)
    total_stock = models.PositiveIntegerField(default=0)
    
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
            # Transliterate name to ASCII if unidecode is available
            if HAS_UNIDECODE:
                transliterated_name = unidecode(self.name)
            else:
                # Fallback: use name as-is and let slugify handle it
                transliterated_name = self.name
            
            base_slug = slugify(transliterated_name)
            
            # If slug is empty after slugify, use UUID fallback
            if not base_slug:
                import uuid
                base_slug = f"product-{uuid.uuid4().hex[:8]}"
            
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name
    
    def is_available(self):
        return self.is_active and self.total_stock > 0
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                                related_name='images')
    image = models.ImageField(upload_to='products/extra/')
