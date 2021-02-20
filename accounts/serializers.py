from rest_framework import serializers
from .models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "email",
            "last_login",
            "date_joined",
        ]
