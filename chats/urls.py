from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('<int:chat_id>/send/', views.send_message, name='send_message'),
    path('<int:chat_id>/messages/', views.get_messages, name='get_messages'),
    path('api/unread-count/', views.unread_count, name='unread_count'),
    path('start/<slug:product_slug>/', views.start_chat_with_owner, name='start_chat_with_owner'),
]
