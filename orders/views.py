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
from main.models import ProductSize
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

    @transaction.atomic
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

            for item in cart.items.select_related('product', 'product_size'):
                logger.debug(f"Processing cart item: product={item.product.name}, size={item.product_size.size.name}, quantity={item.quantity}")
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.product_size,
                    quantity=item.quantity,
                )
                
                # Decrease product stock
                product = item.product
                if product.total_stock >= item.quantity:
                    product.total_stock -= item.quantity
                    
                    # If stock reaches 0, deactivate product
                    if product.total_stock == 0:
                        product.is_active = False
                        logger.info(f"Product {product.name} is now out of stock and deactivated")
                    
                    product.save()
                    logger.debug(f"Updated stock for {product.name}: {product.total_stock} remaining")
                else:
                    logger.warning(f"Insufficient stock for {product.name}: requested {item.quantity}, available {product.total_stock}")

            # Clear cart
            cart.items.all().delete()
            cart.save()

            context = {
                'order': order,
                'success': True,
            }
            
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'orders/partials/order_success.html', context)
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
