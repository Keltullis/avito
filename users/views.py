from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm
from .models import CustomUser, Wishlist
from django.contrib import messages
from main.models import Product, ProductImage, ProductSize, Size
from orders.models import Order
from main.forms import ProductForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:index')
    else:
        form = CustomUserLoginForm()
    return render(request, 'users/login.html', {'form': form})
    

@login_required(login_url='/users/login')
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.headers.get("HX-Request"):
                return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
            return redirect('users:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    latest_orders = orders[:3]

    recommended_products = Product.objects.all().order_by('id')[:3]
    
    user_listings = Product.objects.filter(owner=request.user)
    active_listings_count = user_listings.filter(is_active=True).count()
    total_listings_count = user_listings.count()

    return TemplateResponse(request, 'users/profile.html', {
        'form': form,
        'user': request.user,
        'recommended_products': recommended_products,
        'orders': orders,
        'latest_orders': latest_orders,
        'active_listings_count': active_listings_count,
        'total_listings_count': total_listings_count,
    })


@login_required(login_url='/users/login')
def account_details(request):
    user = CustomUser.objects.get(id=request.user.id)
    return TemplateResponse(request, 'users/partials/account_details.html', {'user': user})


@login_required(login_url='/users/login')
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request, 'users/partials/edit_account_details.html',
                            {'user': request.user, 'form': form})


@login_required(login_url='/users/login')
def update_account_details(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()
            updated_user = CustomUser.objects.get(id=user.id)
            request.user = updated_user
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
            return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
        else:
            return TemplateResponse(request, 'users/partials/edit_account_details.html', {'user': request.user, 'form': form})
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('user:profile')})
    return redirect('users:profile')


def logout_view(request):
    logout(request)
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('main:index')})
    return redirect('main:index')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'users/partials/order_history_full.html', {
            'orders': orders
        })
    return TemplateResponse(request, 'users/partials/order_history_full.html', {
        'orders': orders
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return TemplateResponse(request, 'users/partials/order_detail.html', {'order': order})


@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return TemplateResponse(request, 'users/partials/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, product_slug):
    """Add product to wishlist via AJAX"""
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=product_slug)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': 'Товар добавлен в список желаний'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Товар уже в списке желаний'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def remove_from_wishlist(request, wishlist_id):
    """Remove item from wishlist"""
    if request.method in ['POST', 'DELETE']:
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        wishlist_item.delete()
        
        if request.headers.get('HX-Request'):
            wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
            return TemplateResponse(request, 'users/partials/wishlist.html', {'wishlist_items': wishlist_items})
        
        return JsonResponse({'success': True, 'message': 'Товар удален из списка желаний'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def check_wishlist_status(request, product_slug):
    """Check if product is in user's wishlist"""
    product = get_object_or_404(Product, slug=product_slug)
    in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    return JsonResponse({'in_wishlist': in_wishlist})


@login_required
def create_listing_view(request):
    """Display create listing form"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.is_active = True
            product.save()
            
            images = request.FILES.getlist('additional_images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            sizes = form.cleaned_data.get('sizes')
            if sizes:
                stock_per_size = product.total_stock // len(sizes) if len(sizes) > 0 else product.total_stock
                for size in sizes:
                    ProductSize.objects.create(
                        product=product,
                        size=size,
                        stock=stock_per_size
                    )
            else:
                default_size, created = Size.objects.get_or_create(name='One Size')
                ProductSize.objects.create(
                    product=product,
                    size=default_size,
                    stock=product.total_stock
                )
            
            messages.success(request, 'Объявление успешно создано!')
            if request.headers.get('HX-Request'):
                return HttpResponse(status=200)
            return redirect('users:my_listings')
    else:
        form = ProductForm()
    
    return TemplateResponse(request, 'users/partials/create_listing_form.html', {
        'form': form,
        'sizes': Size.objects.all()
    })


@login_required
def my_listings_view(request):
    """Display user's listings (both active and inactive)"""
    active_listings = Product.objects.filter(owner=request.user, is_active=True).order_by('-created_at')
    inactive_listings = Product.objects.filter(owner=request.user, is_active=False).order_by('-created_at')
    
    return TemplateResponse(request, 'users/partials/my_listings.html', {
        'active_listings': active_listings,
        'inactive_listings': inactive_listings
    })


@login_required
def delete_listing(request, product_id):
    """Delete a listing"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, owner=request.user)
        product.delete()
        messages.success(request, 'Объявление удалено')
        
        if request.headers.get('HX-Request'):
            active_listings = Product.objects.filter(owner=request.user, is_active=True).order_by('-created_at')
            inactive_listings = Product.objects.filter(owner=request.user, is_active=False).order_by('-created_at')
            return TemplateResponse(request, 'users/partials/my_listings.html', {
                'active_listings': active_listings,
                'inactive_listings': inactive_listings
            })
        return redirect('users:my_listings')
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def toggle_listing_status(request, product_id):
    """Toggle listing active status"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, owner=request.user)
        product.is_active = not product.is_active
        product.save()
        
        status = 'активировано' if product.is_active else 'деактивировано'
        messages.success(request, f'Объявление {status}')
        
        if request.headers.get('HX-Request'):
            active_listings = Product.objects.filter(owner=request.user, is_active=True).order_by('-created_at')
            inactive_listings = Product.objects.filter(owner=request.user, is_active=False).order_by('-created_at')
            return TemplateResponse(request, 'users/partials/my_listings.html', {
                'active_listings': active_listings,
                'inactive_listings': inactive_listings
            })
        return redirect('users:my_listings')
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
