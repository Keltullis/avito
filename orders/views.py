from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.views.generic import View
from django.db import transaction
from .forms import OrderForm
from .models import Order, OrderItem
from cart.views import CartMixin
from cart.models import Cart
from main.models import ProductSize, Product
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class CheckoutView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        logger.debug(f"Checkout view: session_key={request.session.session_key}, cart_id={cart.id}, total_items={cart.total_items}")

        if cart.total_items == 0:
            logger.warning("Cart is empty, redirecting to cart page")
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/partials/empty_cart.html', {'message': 'Ваша корзина пуста'})
            return redirect('cart:cart_modal')

        form = OrderForm(user=request.user)
        context = {
            'form': form,
            'cart': cart,
            'cart_items': cart.items.select_related('product', 'product_size__size').order_by('-added_at'),
        }

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/partials/checkout_content.html', context)
        return render(request, 'orders/checkout.html', context)

    def post(self, request):
        cart = self.get_cart(request)
        logger.debug(f"Checkout POST: session_key={request.session.session_key}, cart_id={cart.id}, total_items={cart.total_items}")

        if cart.total_items == 0:
            logger.warning("Cart is empty")
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/partials/empty_cart.html', {'message': 'Ваша корзина пуста'})
            return redirect('cart:cart_modal')

        form = OrderForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Создаем заказ
                    order = Order.objects.create(
                        user=request.user,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        phone=form.cleaned_data['phone'],
                        delivery_address=form.cleaned_data['delivery_address'],
                        group_number=form.cleaned_data['group_number'],
                        email=request.user.email,
                        status='pending',
                    )

                    # Создаем элементы заказа и обновляем количество товара
                    for item in cart.items.select_related('product', 'product_size'):
                        logger.debug(f"Processing cart item: product={item.product.name}, size={item.product_size.size.name}, quantity={item.quantity}, stock={item.product_size.stock}")
                        
                        # Проверяем доступное количество
                        if item.product_size.stock < item.quantity:
                            error_msg = f"Недостаточно товара '{item.product.name}' размера '{item.product_size.size.name}'. Доступно: {item.product_size.stock}, запрошено: {item.quantity}"
                            logger.error(error_msg)
                            raise ValueError(error_msg)
                        
                        # Создаем элемент заказа
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            size=item.product_size,
                            quantity=item.quantity,
                        )
                        
                        # Уменьшаем количество товара в ProductSize
                        item.product_size.stock -= item.quantity
                        item.product_size.save()
                        
                        # Обновляем total_stock в Product
                        product = item.product
                        product.total_stock = sum(ps.stock for ps in product.product_sizes.all())
                        
                        # Если товар закончился, деактивируем его
                        if product.total_stock == 0:
                            product.is_active = False
                        
                        product.save()
                        
                        logger.debug(f"Updated stock for {product.name}: total_stock = {product.total_stock}, is_active = {product.is_active}")

                    # Очищаем корзину
                    cart.items.all().delete()
                    cart.save()

                    context = {
                        'order': order,
                        'success': True,
                    }
                    
                    if request.headers.get('HX-Request'):
                        return TemplateResponse(request, 'orders/partials/order_success.html', context)
                    return TemplateResponse(request, 'orders/partials/order_success.html', context)

            except ValueError as e:
                # Ошибка недостаточного количества товара
                logger.error(f"Insufficient stock error: {e}")
                context = {
                    'form': form,
                    'cart': cart,
                    'cart_items': cart.items.select_related('product', 'product_size__size').order_by('-added_at'),
                    'error_message': str(e),
                }
                if request.headers.get('HX-Request'):
                    return TemplateResponse(request, 'orders/partials/checkout_content.html', context)
                return render(request, 'orders/checkout.html', context)

            except Exception as e:
                # Общая ошибка
                logger.error(f"Order creation error: {e}")
                context = {
                    'form': form,
                    'cart': cart,
                    'cart_items': cart.items.select_related('product', 'product_size__size').order_by('-added_at'),
                    'error_message': 'Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте еще раз.',
                }
                if request.headers.get('HX-Request'):
                    return TemplateResponse(request, 'orders/partials/checkout_content.html', context)
                return render(request, 'orders/checkout.html', context)

        else:
            logger.warning(f"Form validation error: {form.errors}")
            context = {
                'form': form,
                'cart': cart,
                'cart_items': cart.items.select_related('product', 'product_size__size').order_by('-added_at'),
                'error_message': 'Пожалуйста, исправьте ошибки в форме.',
            }
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/partials/checkout_content.html', context)
            return render(request, 'orders/checkout.html', context)


@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class OrderHistoryView(View):
    """View for displaying order history"""
    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
        
        context = {
            'orders': orders,
        }
        
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'orders/partials/order_history.html', context)
        return render(request, 'orders/order_history.html', context)


@method_decorator(login_required(login_url='/users/login'), name='dispatch')
class OrderDetailView(View):
    """View for displaying order details in modal"""
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        context = {
            'order': order,
        }
        
        return TemplateResponse(request, 'orders/partials/order_detail_modal.html', context)