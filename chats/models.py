from django.db import models
from django.conf import settings


class Chat(models.Model):
    """Чат между двумя пользователями"""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        users = list(self.participants.all())
        if len(users) >= 2:
            return f"Чат между {users[0].username} и {users[1].username}"
        return f"Чат #{self.id}"

    def get_other_user(self, user):
        """Получить собеседника"""
        return self.participants.exclude(id=user.id).first()

    def get_last_message(self):
        """Получить последнее сообщение"""
        return self.messages.first()

    def get_unread_count(self, user):
        """Количество непрочитанных сообщений для пользователя"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """Сообщение в чате"""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.text[:50]}"
