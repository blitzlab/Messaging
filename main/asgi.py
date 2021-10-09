"""
ASGI config for main project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack

from channels.routing import ProtocolTypeRouter, URLRouter

from chat.consumers import ChatConsumer

from django.urls import path

# import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

# application = get_asgi_application()

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": get_asgi_application(),

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path('chat/<str:room_id>/<int:page_number>/', ChatConsumer.as_asgi()),
            ]
        )
    ),
})
