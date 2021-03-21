from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Family, Student, Field


class FamilySerializer(serializers.HyperlinkedModelSerializer):
    first_name = SerializerMethodField()
    last_name = SerializerMethodField()
    num_children = SerializerMethodField()

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
            "num_children",
        ]

    def get_num_children(self, obj):
        return Student.objects.filter(family=obj.id, role=Student.CHILD).count()

    def get_first_name(self, obj):
        return obj.parent.first_name if obj.parent else ""

    def get_last_name(self, obj):
        return obj.parent.last_name if obj.parent else ""


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    family = serializers.HyperlinkedRelatedField(
        view_name="families-detail", read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "role",
            "family",
            "information",
        ]
        read_only_fields = ["role"]


class FamilyDetailSerializer(serializers.HyperlinkedModelSerializer):
    parent = StudentSerializer()
    children = StudentSerializer(many=True)
    guests = StudentSerializer(many=True)

    class Meta:
        model = Family
        fields = [
            "id",
            "email",
            "phone_number",
            "address",
            "preferred_comms",
            "parent",
            "children",
            "guests",
        ]

    def create(self, validated_data):
        parent_data = validated_data.pop("parent")
        children_data = validated_data.pop("children", [])
        guests_data = validated_data.pop("guests", [])

        with transaction.atomic():
            family = Family.objects.create(**validated_data)
            Student.objects.bulk_create(
                Student(**student_data, family=family)
                for student_data in [parent_data] + children_data + guests_data
            )
            family.parent = Student.objects.get(family=family, role=Student.PARENT)
            family.save()

        return family

    def to_internal_value(self, data):
        parent_data = data.get("parent")
        if parent_data is None:
            raise serializers.ValidationError("Parent is a required field")
        parent_data["role"] = Student.PARENT

        children_data = data.get("children", [])
        for child_data in children_data:
            child_data["role"] = Student.CHILD

        guests_data = data.get("guests", [])
        for guest_data in guests_data:
            guest_data["role"] = Student.GUEST

        return data


class FieldSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Field
        fields = [
            "id",
            "role",
            "name",
            "question",
            "question_type",
            "is_default",
            "order",
        ]
