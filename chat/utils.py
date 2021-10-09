import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def trigger_welcome_message(sender_id, receiver_id):
    data = {
        "type": "welcome_message",
        "message": "Hello there!",
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "timeout": 45
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)('task', data)



def broadcast_msg_to_chat(msg, group_name, user='admin', event_type='broadcast_message'):
    channel_layer = get_channel_layer()
    actual_message = json.dumps({'msg': msg, 'user': user})
    broadcast_data = {
        'type': event_type,
        'message': actual_message
    }
    async_to_sync(channel_layer.group_send)(group_name, broadcast_data)
    
from django.core.serializers.python import Serializer
class ChatMessageEncoder(Serializer):
    def get_dump_object(self, obj):
        data = {}
        data.update({"message_id":str(obj.id)})
        data.update({"message":str(obj.message)})
        data.update({"read":str(obj.read)})
        data.update({"user":str(obj.user.username)})
        return data
    
class MessageSenderEncoder(Serializer):
    def get_dump_object(self, obj):
        data = {}
        data.update({"name":obj.name})
        data.update({"email":obj.email})
        return data