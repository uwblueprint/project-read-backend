from rest_framework import serializers
from .models import Family, FamilyInfo, ChildInfo


class FamilySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Family
        fields = [
            "id",
            "email",
            "phone_number",
            "address",
            "preferred_comms",
        ]


class FamilyInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FamilyInfo
        fields = [
            "id",
            "name",
            "question",
        ]


class ChildInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChildInfo
        fields = [
            "id",
            "name",
            "question",
        ]
