from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Family, FamilyInfo, ChildInfo


class FamilySerializer(serializers.HyperlinkedModelSerializer):
    first_name = SerializerMethodField()
    last_name = SerializerMethodField()

    class Meta:
        model = Family
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "preferred_comms",
        ]

    def get_first_name(self, obj):
        return obj.parent.first_name if obj.parent else ""

    def get_last_name(self, obj):
        return obj.parent.last_name if obj.parent else ""


class FamilyDetailSerializer(serializers.HyperlinkedModelSerializer):
    first_name = SerializerMethodField()
    last_name = SerializerMethodField()
    parent_fields = SerializerMethodField()

    class Meta:
        model = Family
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "preferred_comms",
            "parent_fields",
        ]

    def get_first_name(self, obj):
        return obj.parent.first_name if obj.parent else ""

    def get_last_name(self, obj):
        return obj.parent.last_name if obj.parent else ""

    def get_parent_fields(self, obj):
        return obj.parent.information if obj.parent else {}


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
