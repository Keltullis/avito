from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import ProductModeration, ModerationStatus
from main.models import Product


def is_moderator(user):
    """Проверка, является ли пользователь модератором"""
    return user.is_authenticated and (user.is_moderator or user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_moderator)
def moderator_dashboard(request):
    """Главная страница модератора со статистикой"""
    pending_count = ProductModeration.objects.filter(status=ModerationStatus.PENDING).count()
    approved_count = ProductModeration.objects.filter(status=ModerationStatus.APPROVED).count()
    rejected_count = ProductModeration.objects.filter(status=ModerationStatus.REJECTED).count()
    
    recent_pending = ProductModeration.objects.filter(
        status=ModerationStatus.PENDING
    ).select_related('product', 'product__owner')[:5]
    
    return TemplateResponse(request, 'moderator/dashboard.html', {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'recent_pending': recent_pending,
    })


@login_required
@user_passes_test(is_moderator)
def pending_listings(request):
    """Список объявлений на модерации"""
    listings = ProductModeration.objects.filter(
        status=ModerationStatus.PENDING
    ).select_related('product', 'product__owner').order_by('-created_at')
    
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'moderator/partials/pending_listings.html', {
            'listings': listings
        })
    
    return TemplateResponse(request, 'moderator/partials/pending_listings.html', {
        'listings': listings
    })


@login_required
@user_passes_test(is_moderator)
def approved_listings(request):
    """Список одобренных объявлений"""
    listings = ProductModeration.objects.filter(
        status=ModerationStatus.APPROVED
    ).select_related('product', 'product__owner').order_by('-moderated_at')
    
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'moderator/partials/approved_listings.html', {
            'listings': listings
        })
    
    return TemplateResponse(request, 'moderator/partials/approved_listings.html', {
        'listings': listings
    })


@login_required
@user_passes_test(is_moderator)
def rejected_listings(request):
    """Список отклоненных объявлений"""
    listings = ProductModeration.objects.filter(
        status=ModerationStatus.REJECTED
    ).select_related('product', 'product__owner').order_by('-moderated_at')
    
    if request.headers.get('HX-Request'):
        return TemplateResponse(request, 'moderator/partials/rejected_listings.html', {
            'listings': listings
        })
    
    return TemplateResponse(request, 'moderator/partials/rejected_listings.html', {
        'listings': listings
    })


@login_required
@user_passes_test(is_moderator)
def approve_listing(request, product_id):
    """Одобрить объявление"""
    moderation = get_object_or_404(
        ProductModeration,
        product_id=product_id,
        status=ModerationStatus.PENDING
    )
    
    # Обновляем статус модерации
    moderation.status = ModerationStatus.APPROVED
    moderation.moderator = request.user
    moderation.moderated_at = timezone.now()
    moderation.save()
    
    product = moderation.product
    if product.total_stock > 0:
        product.is_active = True
        product.save()
        messages.success(request, f'Объявление "{product.name}" одобрено и опубликовано')
    else:
        product.is_active = False
        product.save()
        messages.warning(request, f'Объявление "{product.name}" одобрено, но не опубликовано (остаток = 0)')
    
    if request.headers.get('HX-Request'):
        # Возвращаем обновленный список
        listings = ProductModeration.objects.filter(
            status=ModerationStatus.PENDING
        ).select_related('product', 'product__owner').order_by('-created_at')
        return TemplateResponse(request, 'moderator/partials/pending_listings.html', {
            'listings': listings
        })
    
    return redirect('moderator:pending_listings')


@login_required
@user_passes_test(is_moderator)
def reject_listing(request, product_id):
    """Отклонить объявление"""
    moderation = get_object_or_404(
        ProductModeration,
        product_id=product_id,
        status=ModerationStatus.PENDING
    )
    
    rejection_reason = request.POST.get('rejection_reason', '')
    
    # Обновляем статус модерации
    moderation.status = ModerationStatus.REJECTED
    moderation.moderator = request.user
    moderation.moderated_at = timezone.now()
    moderation.rejection_reason = rejection_reason
    moderation.save()
    
    # Деактивируем продукт
    product = moderation.product
    product.is_active = False
    product.save()
    
    messages.success(request, f'Объявление "{product.name}" отклонено')
    
    if request.headers.get('HX-Request'):
        # Возвращаем обновленный список
        listings = ProductModeration.objects.filter(
            status=ModerationStatus.PENDING
        ).select_related('product', 'product__owner').order_by('-created_at')
        return TemplateResponse(request, 'moderator/partials/pending_listings.html', {
            'listings': listings
        })
    
    return redirect('moderator:pending_listings')


@login_required
@user_passes_test(is_moderator)
def listing_detail(request, product_id):
    """Детальный просмотр объявления для модерации"""
    moderation = get_object_or_404(
        ProductModeration,
        product_id=product_id
    )
    product = moderation.product
    
    return TemplateResponse(request, 'moderator/partials/listing_detail.html', {
        'moderation': moderation,
        'product': product,
    })
