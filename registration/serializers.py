from django.db import models, transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Family, Student, Field
from enrolments.models import Session, Enrolment
from .validators import validate_student_information_role


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    family = serializers.HyperlinkedRelatedField(
        view_name="family-detail", read_only=True
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

    def validate(self, attrs):
        validate_student_information_role(
            attrs.get("information", {}),
            attrs["role"],
        )
        return super().validate(attrs)


class FamilySerializer(serializers.HyperlinkedModelSerializer):
    parent = StudentSerializer()
    num_children = SerializerMethodField()
    enrolled = SerializerMethodField()
    current_class = SerializerMethodField()
    status = SerializerMethodField()
    most_recent_session = (
        Session.objects.order_by("-start_date")[0]
        if Session.objects.order_by("-start_date")
        else None
    )

    class Meta:
        model = Family
        fields = [
            "id",
            "parent",
            "email",
            "phone_number",
            "address",
            "preferred_comms",
            "num_children",
            "enrolled",
            "current_class",
            "status",
        ]

    def get_num_children(self, obj):
        return obj.children.count()

    def get_enrolled(self, obj):
        most_recent_enrolment = Enrolment.objects.filter(
            family=obj, session=self.most_recent_session
        )
        return "Yes" if most_recent_enrolment else "No"

    def get_current_class(self, obj):
        most_recent_enrolment = Enrolment.objects.filter(
            family=obj, session=self.most_recent_session
        )
        return (
            most_recent_enrolment[0].enrolled_class.name
            if most_recent_enrolment
            else "N/A"
        )

    def get_status(self, obj):
        most_recent_enrolment = Enrolment.objects.filter(
            family=obj, session=self.most_recent_session
        )
        return (
            most_recent_enrolment[0].status if most_recent_enrolment else "Unassigned"
        )


class FamilyDetailSerializer(serializers.HyperlinkedModelSerializer):
    parent = StudentSerializer()
    children = StudentSerializer(many=True)
    guests = StudentSerializer(many=True)

    class Meta:
        model = Family
        fields = [
            "id",
            "email",
            "home_number",
            "cell_number",
            "work_number",
            "preferred_number",
            "address",
            "preferred_comms",
            "parent",
            "children",
            "guests",
        ]

    def create(self, validated_data):
        students = validated_data.pop("students")
        with transaction.atomic():
            family = Family.objects.create(**validated_data)
            Student.objects.bulk_create(
                Student(**student, family=family) for student in students
            )
            # parent is validated in to_internal_value, so there should always be a parent created
            family.parent = Student.objects.get(family=family, role=Student.PARENT)
            family.save()

        return family

    def to_internal_value(self, data):
        parent = data.pop("parent", {})
        if not len(parent):
            raise serializers.ValidationError("Parent is a required field")
        parent["role"] = Student.PARENT

        children = data.pop("children", [])
        for child in children:
            child["role"] = Student.CHILD

        guests = data.pop("guests", [])
        for guest in guests:
            guest["role"] = Student.GUEST

        data["students"] = [parent] + children + guests
        return data

    def validate(self, attrs):
        if not all(
            StudentSerializer(data=student).is_valid() for student in attrs["students"]
        ):
            raise serializers.ValidationError("Student data is invalid")
        return super().validate(attrs)


class FieldListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        iterable = data.all() if isinstance(data, models.Manager) else data
        fields = dict()

        for role_choice in Field.ROLE_CHOICES:
            role = role_choice[0]
            fields[f"{role.lower()}_fields"] = super().to_representation(
                iterable.filter(role=role).order_by("order")
            )

        return [fields]


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
        list_serializer_class = FieldListSerializer
