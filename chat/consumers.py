from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.db import database_sync_to_async
from .models import Thread, ChatMessage
from django.contrib.auth import get_user_model
import json
from django.core import serializers
from chat.utils import ChatMessageEncoder, MessageSenderEncoder
from django.core.paginator import Paginator
from .constants import *

User = get_user_model()

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        print("ChatConsumer: connect: " + str(self.scope["user"]))
        # if self.scope["user"].is_authenticated:
        # Use username to connect chat
        query_params = self.scope['url_route']['kwargs']
        self.room_id = query_params['room_id']
        page_number = query_params['page_number'] if query_params['page_number'] else 1
        # user = self.scope['user']
        
        self.thread_obj = await self.get_thread(self.room_id)
        
        if self.thread_obj is None:
            print("Invalid room ID")
            return None
        
        print(self.thread_obj)
        # self.cfe_chat_thread = thread_obj
        
        self.room_name = self.thread_obj.room_name # group
        
        print((self.room_name))
        
        # let everyone connect. But limit read/write to authenticated users
        
        await self.accept()
        
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name,
        )
        
        qs = ChatMessage.objects.filter(thread=self.thread_obj)
        
        payload = await self.get_room_chat_messages(qs, page_number)
        
        # print(qs.values)
        # # data = serializers.serialize('json', list(qs))
        # 
        await self.send_json({
            "type":"chat_messages",
            "messages":payload
        })
        
        # the room_id will define what it means to be "connected". If it is not None, then the user is connected.
        # 
        self.room_id = None
        
    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        
        print("ChatConsumer: receive_json")
        try:
            sender_username = content.get("username")
            message = content.get("message")
            print((sender_username))
            print((message))
            sender = await self.sender_valid(sender_username)
            if sender is None:
                print("Sender is not associated with to room")
                await self.send_json({
                    "message":"Sender is not associated with to room"
                })
                pass
            
            await self.create_chat_message(sender, message)
            print("Saved message")
            
            await self.send_json({
				"user_info":{
						"name":sender.name, 
						"username":sender.username,
						"avatar":sender.profile_picture.url
				},
				"message":message
			})
        except Exception as e:
            print(e)
            pass
    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave the room
        print("ChatConsumer: disconnect")
        pass
    
    
    @database_sync_to_async
    def sender_valid(self, username):
        if self.thread_obj.first.username == username:
            user = self.thread_obj.first
        elif self.thread_obj.second.username == username:
            user = self.thread_obj.second
        else:
            user = None
        return user
    
    @database_sync_to_async
    def create_chat_message(self, sender, message):
        thread = self.thread_obj
        return ChatMessage.objects.create(thread=thread, user=sender, message=message)
    
    @database_sync_to_async
    def get_thread(self, room_id):
        return Thread.objects.get_thread_room_id(room_id)
    
    
    @database_sync_to_async
    def get_room_chat_messages(self, qs, page_number):
        try:
            p = Paginator(qs, NUMBER_OF_ITEMS_PER_REQUEST)
            
            payload = {}
            messages_data = None
            new_page_number = int(page_number)
            if new_page_number <= p.num_pages:
                new_page_number = new_page_number + 1
                s = ChatMessageEncoder()
                payload['messages'] = s.serialize(p.page(page_number).object_list)
            else:
                payload['messages'] = "None"
            payload['next_page_number'] = new_page_number
            return json.dumps(payload)
        except Exception as e:
            print("EXCEPTION: " + str(e))
            return None


	

