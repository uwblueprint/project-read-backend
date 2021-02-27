from rest_framework import serializers
from .models import Family, FamilyInfo


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
            "active",
        ]
