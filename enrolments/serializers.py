from rest_framework import serializers
from .models import Session, Class


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "season",
            "year",
        ]


class ClassListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "name", "facilitator_id"]


class SessionDetailsSerializer(serializers.HyperlinkedModelSerializer):
    classes = ClassListSerializer(many=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "season",
            "year",
            "classes",
        ]
