from django.urls import path
from chat.api.v1.viewsets import InitiateChatView, UpdateReadStatusView

app_name = "chat"

urlpatterns = [
    path('initiate-chat/', InitiateChatView.as_view(), name="initiate_chat"),
    path('update-read-status/', UpdateReadStatusView.as_view(), name="update_read_status"),
]