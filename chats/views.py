from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Max
from django.conf import settings
from .models import Chat, Message


@login_required
def chat_list(request):
    """Список всех чатов пользователя"""
    chats = Chat.objects.filter(participants=request.user).prefetch_related('participants', 'messages')
    
    # Добавляем информацию о последнем сообщении и количестве непрочитанных
    chat_data = []
    for chat in chats:
        other_user = chat.get_other_user(request.user)
        last_message = chat.get_last_message()
        unread_count = chat.get_unread_count(request.user)
        
        chat_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    context = {
        'chat_data': chat_data,
    }
    return render(request, 'chats/chat_list.html', context)


@login_required
def chat_detail(request, chat_id):
    """Детальный вид чата с сообщениями"""
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    
    other_user = chat.get_other_user(request.user)
    
    # Отмечаем все сообщения как прочитанные
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Получаем сообщения (по 50 последних)
    messages = chat.messages.all()[:50]
    
    context = {
        'chat': chat,
        'other_user': other_user,
        'messages': reversed(messages),  # Показываем в хронологическом порядке
    }
    return render(request, 'chats/chat_detail.html', context)


@login_required
def send_message(request, chat_id):
    """Отправка сообщения через HTMX"""
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
        text = request.POST.get('message', '').strip()
        
        if text:
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text
            )
            
            # Обновляем время последнего обновления чата
            chat.save()
            
            # Возвращаем partial с новым сообщением
            context = {
                'message': message,
                'is_own': True,
            }
            return render(request, 'chats/partials/message_item.html', context)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def get_messages(request, chat_id):
    """Получение сообщений для HTMX polling"""
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    messages = chat.messages.all()[:50]
    
    # Отмечаем новые сообщения как прочитанные
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    context = {
        'messages': reversed(messages),
        'current_user': request.user,
    }
    return render(request, 'chats/partials/message_list.html', context)


@login_required
def unread_count(request):
    """API для получения количества непрочитанных сообщений"""
    chats = Chat.objects.filter(participants=request.user)
    total_unread = 0
    
    for chat in chats:
        total_unread += chat.get_unread_count(request.user)
    
    return JsonResponse({'unread_count': total_unread})


@login_required
def start_chat_with_owner(request, product_slug):
    """Создать или получить чат с владельцем продукта"""
    from main.models import Product  # Import here to avoid circular import
    
    product = get_object_or_404(Product, slug=product_slug)
    
    owner = getattr(product, 'owner', None) or getattr(product, 'user', None)
    
    if not owner:
        return JsonResponse({'error': 'У продукта нет владельца'}, status=400)
    
    # Не позволяем пользователю начать чат с самим собой
    if owner == request.user:
        return redirect('main:index')
    
    # Проверяем, существует ли уже чат между этими пользователями
    existing_chat = Chat.objects.filter(participants=request.user).filter(participants=owner).first()
    
    if existing_chat:
        # Если чат существует, перенаправляем на него
        return redirect('chats:chat_detail', chat_id=existing_chat.id)
    
    # Создаем новый чат
    new_chat = Chat.objects.create()
    new_chat.participants.add(request.user, owner)
    
    # Перенаправляем на новый чат
    return redirect('chats:chat_detail', chat_id=new_chat.id)
