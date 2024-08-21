from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from api.v1.serializers.user_serializer import (CustomUserSerializer, 
                                                SubscriptionSerializer, 
                                                BalanceSerializer,
                                                ChangeBalanceSerializer)

from users.models import Subscription, Balance

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Пользователи."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = (permissions.IsAdminUser,)

class SubcriptionViewSet(viewsets.ModelViewSet):
    """Подписки (покупки)"""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    http_method_names = ["get", "head", "options"]  
    permission_classes = (permissions.IsAdminUser,)

class BalancesViewset(viewsets.ModelViewSet):
    """Баланс и Бонусы."""
 
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    permission_classes = (permissions.IsAdminUser,)
    http_method_names = ["get", "head", "options", "patch"]
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BalanceSerializer
        return ChangeBalanceSerializer