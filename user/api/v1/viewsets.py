from rest_framework import viewsets
from django.contrib.auth.models import User
from user.api.v1 import serializers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "pk"
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer