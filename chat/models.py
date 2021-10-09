from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from .utils import broadcast_msg_to_chat, trigger_welcome_message

from django.contrib.auth import get_user_model

User = get_user_model()

def reference_id_generator(lenght):
    import random, string
    id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(lenght))
    return id

class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_create(self, user, other_user): # get_or_create
        username = user.username
        other_username = other_user.username
        if username == other_username:
            return None
        
        qlookup1 = Q(first__username=username) & Q(second__username=other_username)
        qlookup2 = Q(first__username=other_username) & Q(second__username=username)
        
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = user.__class__
            # user2 = Klass.objects.get(username=other_username)
            if user != other_user:
                obj = self.model(
                        unique_id = reference_id_generator(32),
                        first=user, 
                        second=other_user
                    )
                obj.save()
                return obj, True
            return None, False
        
    def get_thread_room_id(self, room_id):
        thread = self.get_queryset().filter(unique_id=room_id).first()
        if not thread:
            return None
        return thread


class Thread(models.Model):
    unique_id = models.CharField("Thread ID", max_length=50, null=True)
    first = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_thread_first')
    second = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_thread_second')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = ThreadManager()

    def __str__(self):
        return self.unique_id if self.unique_id is not None else str(self.pk)
    
    
    @property
    def room_name(self):
        return f'room_{self.unique_id}'

    def broadcast(self, msg=None):
        if msg is not None:
            broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
            return True
        return False



class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, related_name="chat_message", blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, verbose_name='sender', on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.message)


# Signal
@receiver(post_save, sender=User)
def new_user_receiver(sender, instance, created, *args ,**kargs):
    if created:
        sender_id = 1 # admin user, main sender
        receiver_id = instance.id
        trigger_welcome_message(sender_id, receiver_id)
