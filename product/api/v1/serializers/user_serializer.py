from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Subscription, Balance

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    balance = serializers.SerializerMethodField(read_only=True)

    def get_balance(self, obj):
        return obj.balance.amount

    class Meta:
        model = User
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        model = Subscription
        fields = '__all__'

class BalanceSerializer(serializers.ModelSerializer):
    """Сериализатор баланса."""

    class Meta:
        model = Balance
        fields = '__all__'

class ChangeBalanceSerializer(serializers.ModelSerializer):
    """Изменения баланса."""

    class Meta:
        model = Balance
        fields = (
            'amount',
        )