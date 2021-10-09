from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from chat.models import Thread, ChatMessage

class InitiateChatView(APIView):
    def post(self, request):
        try:
            if request.data.get("username") is None:
                return Response("Username is required", status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            print(user)
            other_user = User.objects.get(username=request.data.get("username"))
            
            get_thread = Thread.objects.get_or_create(user, other_user)[0]
            
            return Response({"room_id":get_thread.unique_id})
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateReadStatusView(APIView):
    def put(self, request):
        try:
            message_id = request.data.get("message_id")
            if not message_id:
                raise Exception("Message ID is required")
            
            ChatMessage.objects.filter(pk=message_id).update(read=True)
            
            return Response("success")
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        