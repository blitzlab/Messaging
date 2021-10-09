from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.api.v1 import viewsets

app_name = "user"

router = DefaultRouter()

router.register(r'register', viewsets.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]