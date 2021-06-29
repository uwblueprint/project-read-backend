from rest_framework import serializers
from .models import User
from firebase_admin import auth


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


class UserCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
        ]

    def create(self, validated_data):
        try:
            firebase_user = auth.create_user(email=validated_data["email"])
        except auth.EmailAlreadyExistsError:
            raise serializers.ValidationError(
                detail="user already exists in Firebase", code="default_firebase_user"
            )

        try:
            user = User.objects.create(**validated_data, firebase_uid=firebase_user.uid)
        except Exception as e:
            auth.delete_user(firebase_user.uid)
            raise e

        return user
