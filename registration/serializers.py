from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .constants import family_detail_constant_fields
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
        fields = list(family_detail_constant_fields)

    def get_first_name(self, obj):
        return obj.parent.first_name if obj.parent else ""

    def get_last_name(self, obj):
        return obj.parent.last_name if obj.parent else ""

    def get_parent_fields(self, obj):
        parent_fields = {}
        if obj.parent:
            field_responses = {
                info["id"]: info["response"] for info in obj.parent.information
            }
            fields = FamilyInfo.objects.filter(id__in=field_responses.keys())
            parent_fields = {
                field.name: field_responses.get(field.id) for field in fields
            }
        return parent_fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        parent_fields_representation = representation.pop("parent_fields")
        for key in parent_fields_representation:
            representation[key] = parent_fields_representation[key]
        return representation


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
