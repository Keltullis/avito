from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm, EmailVerificationForm
from .models import CustomUser, Wishlist
from django.contrib import messages
from main.models import Product, ProductImage, ProductSize, Size
from orders.models import Order
from main.forms import ProductForm
from moderator.models import ProductModeration, ModerationStatus
import random
from django.core.mail import send_mail
from django.conf import settings


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Generate 6-digit verification code
            verification_code = str(random.randint(100000, 999999))
            
            # Store registration data and code in session
            request.session['registration_data'] = {
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'password1': form.cleaned_data['password1'],
                'verification_code': verification_code,
            }
            
            # Send verification email
            try:
                send_mail(
                    'Подтверждение регистрации',
                    f'Ваш код подтверждения: {verification_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [form.cleaned_data['email']],
                    fail_silently=False,
                )
                messages.success(request, 'Код подтверждения отправлен на вашу почту')
            except Exception as e:
                messages.error(request, f'Ошибка отправки email: {str(e)}')
                # For development - show code in console
                print(f'[v0] Verification code for {form.cleaned_data["email"]}: {verification_code}')
            
            return redirect('users:verify_email')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def verify_email(request):
    # Check if registration data exists in session
    if 'registration_data' not in request.session:
        messages.error(request, 'Данные регистрации не найдены')
        return redirect('users:register')
    
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            registration_data = request.session.get('registration_data')
            stored_code = registration_data.get('verification_code')
            
            if entered_code == stored_code:
                # Create user
                user = CustomUser.objects.create_user(
                    email=registration_data['email'],
                    first_name=registration_data['first_name'],
                    last_name=registration_data['last_name'],
                    password=registration_data['password1']
                )
                
                # Clear session data
                del request.session['registration_data']
                
                # Log user in
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Регистрация успешно завершена!')
                return redirect('main:index')
            else:
                messages.error(request, 'Неверный код подтверждения')
    else:
        form = EmailVerificationForm()
    
    email = request.session.get('registration_data', {}).get('email', '')
    return render(request, 'users/verify_email.html', {'form': form, 'email': email})


def resend_verification_code(request):
    if 'registration_data' not in request.session:
        return JsonResponse({'success': False, 'message': 'Данные регистрации не найдены'})
    
    # Generate new code
    verification_code = str(random.randint(100000, 999999))
    registration_data = request.session['registration_data']
    registration_data['verification_code'] = verification_code
    request.session['registration_data'] = registration_data
    
    # Send email
    try:
        send_mail(
            'Подтверждение регистрации',
            f'Ваш новый код подтверждения: {verification_code}',
            settings.DEFAULT_FROM_EMAIL,
            [registration_data['email']],
            fail_silently=False,
        )
        print(f'[v0] New verification code for {registration_data["email"]}: {verification_code}')
        return JsonResponse({'success': True, 'message': 'Новый код отправлен на вашу почту'})
    except Exception as e:
        print(f'[v0] Error sending email: {str(e)}')
        print(f'[v0] Verification code: {verification_code}')
        return JsonResponse({'success': False, 'message': f'Ошибка отправки: {str(e)}'})



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
    orders_as_buyer = list(Order.objects.filter(user=request.user))
    orders_as_seller = list(Order.objects.filter(
        items__product__owner=request.user
    ).distinct())
    
    # Combine both lists and remove duplicates by converting to set of IDs, then query again
    order_ids = set([o.id for o in orders_as_buyer] + [o.id for o in orders_as_seller])
    orders = Order.objects.filter(id__in=order_ids).order_by('-created_at')
    
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'users/partials/order_history_full.html', {
            'orders': orders
        })
    return TemplateResponse(request, 'users/partials/order_history_full.html', {
        'orders': orders
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product__owner'), 
        id=order_id
    )
    
    # Check if user is buyer or seller of any item
    is_buyer = order.user == request.user
    is_seller = order.items.filter(product__owner=request.user).exists()
    
    if not (is_buyer or is_seller):
        return HttpResponse("Доступ запрещен", status=403)
    
    return TemplateResponse(request, 'users/partials/order_detail.html', {
        'order': order,
        'is_buyer': is_buyer,
        'is_seller': is_seller
    })


@login_required(login_url='/users/login')
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return TemplateResponse(request, 'users/partials/wishlist.html', {'wishlist_items': wishlist_items})


@login_required(login_url='/users/login')
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


@login_required(login_url='/users/login')
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


@login_required(login_url='/users/login')
def check_wishlist_status(request, product_slug):
    """Check if product is in user's wishlist"""
    product = get_object_or_404(Product, slug=product_slug)
    in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    return JsonResponse({'in_wishlist': in_wishlist})


@login_required(login_url='/users/login')
def create_listing_view(request):
    """Display create listing form"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.is_active = False
            product.save()
            
            images = request.FILES.getlist('additional_images')[:5]
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            no_size = request.POST.get('no_size')
            custom_size_value = request.POST.get('custom_size')
            
            if no_size:
                no_size_obj, created = Size.objects.get_or_create(name='Нет размера')
                ProductSize.objects.create(
                    product=product,
                    size=no_size_obj,
                    stock=product.total_stock
                )
            elif custom_size_value and custom_size_value.strip():
                custom_size_obj, created = Size.objects.get_or_create(name=custom_size_value.strip())
                ProductSize.objects.create(
                    product=product,
                    size=custom_size_obj,
                    stock=product.total_stock
                )
            else:
                sizes = form.cleaned_data.get('sizes')
                if sizes:
                    stock_per_size = product.total_stock // len(sizes) if len(sizes) > 0 else product.total_stock
                    for size in sizes:
                        if size.name != 'One Size':
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
            
            ProductModeration.objects.create(
                product=product,
                status=ModerationStatus.PENDING
            )
            
            messages.success(request, 'Объявление отправлено на модерацию!')
            if request.headers.get('HX-Request'):
                return HttpResponse(status=200)
            return redirect('users:my_listings')
    else:
        form = ProductForm()
    
    return TemplateResponse(request, 'users/partials/create_listing_form.html', {
        'form': form,
        'sizes': Size.objects.all()
    })


@login_required(login_url='/users/login')
def my_listings_view(request):
    """Display user's listings by moderation status"""
    user_products = Product.objects.filter(owner=request.user).select_related('moderation')
    
    approved_listings = []
    pending_listings = []
    rejected_listings = []
    
    for product in user_products:
        try:
            if product.moderation.status == ModerationStatus.APPROVED:
                approved_listings.append(product)
            elif product.moderation.status == ModerationStatus.PENDING:
                pending_listings.append(product)
            elif product.moderation.status == ModerationStatus.REJECTED:
                rejected_listings.append(product)
        except ProductModeration.DoesNotExist:
            ProductModeration.objects.create(
                product=product,
                status=ModerationStatus.APPROVED
            )
            product.is_active = True
            product.save()
            approved_listings.append(product)
    
    return TemplateResponse(request, 'users/partials/my_listings.html', {
        'approved_listings': approved_listings,
        'pending_listings': pending_listings,
        'rejected_listings': rejected_listings,
    })


@login_required(login_url='/users/login')
def delete_listing(request, product_id):
    """Delete a listing"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, owner=request.user)
        product.delete()
        messages.success(request, 'Объявление удалено')
        
        if request.headers.get('HX-Request'):
            user_products = Product.objects.filter(owner=request.user).select_related('moderation')
            
            approved_listings = []
            pending_listings = []
            rejected_listings = []
            
            for prod in user_products:
                try:
                    if prod.moderation.status == ModerationStatus.APPROVED:
                        approved_listings.append(prod)
                    elif prod.moderation.status == ModerationStatus.PENDING:
                        pending_listings.append(prod)
                    elif prod.moderation.status == ModerationStatus.REJECTED:
                        rejected_listings.append(prod)
                except ProductModeration.DoesNotExist:
                    ProductModeration.objects.create(
                        product=prod,
                        status=ModerationStatus.APPROVED
                    )
                    prod.is_active = True
                    prod.save()
                    approved_listings.append(prod)
            
            return TemplateResponse(request, 'users/partials/my_listings.html', {
                'approved_listings': approved_listings,
                'pending_listings': pending_listings,
                'rejected_listings': rejected_listings,
            })
        return redirect('users:my_listings')
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
