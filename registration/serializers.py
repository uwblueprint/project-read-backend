from django.db import models, transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Family, Student, Field
from .validators import validate_student_information_role, validate_field_order
from enrolments.serializers import EnrolmentSerializer


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
            "date_of_birth",
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
    children = StudentSerializer(many=True)
    guests = StudentSerializer(many=True)
    enrolment = SerializerMethodField()

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
            "children",
            "guests",
            "enrolment",
        ]

    def get_num_children(self, obj):
        return obj.children.count()

    def get_enrolment(self, obj):
        enrolment = self.context.get("enrolment")
        if enrolment is not None:
            return enrolment

        if obj.current_enrolment is not None:
            return EnrolmentSerializer(obj.current_enrolment).data

        return None


class FamilyDetailSerializer(serializers.HyperlinkedModelSerializer):
    parent = StudentSerializer()
    children = StudentSerializer(many=True)
    guests = StudentSerializer(many=True)
    enrolments = EnrolmentSerializer(many=True)

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
            "notes",
            "enrolments",
            "interactions",
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

    def update(self, instance, validated_data):
        validated_data.pop("enrolments")
        students_data = validated_data.pop("students")
        students = (
            [instance.parent]
            + list(instance.children.all())
            + list(instance.guests.all())
        )

        existing_students = Student.objects.filter(
            id__in=[student.id for student in students]
        )

        students_to_delete = existing_students.difference(
            Student.objects.filter(id__in=[student["id"] for student in students_data])
        )
        # TODO: change deletion of students to soft delete
        for student in students_to_delete:
            Student.objects.filter(id=student.id).delete()

        for student_data in students_data:
            student = Student.objects.filter(id=student_data["id"])
            if student.exists():
                student.update(
                    first_name=student_data["first_name"],
                    last_name=student_data["last_name"],
                    date_of_birth=student_data["date_of_birth"],
                    information=student_data["information"],
                )
            else:
                Student.objects.create(
                    first_name=student_data["first_name"],
                    last_name=student_data["last_name"],
                    role=student_data["role"],
                    family=instance,
                    date_of_birth=student_data["date_of_birth"],
                    information=student_data["information"],
                )

        super().update(instance, validated_data)
        instance.refresh_from_db()
        return instance

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


class FamilySearchSerializer(serializers.HyperlinkedModelSerializer):
    first_name = SerializerMethodField()
    last_name = SerializerMethodField()
    num_children = SerializerMethodField()

    class Meta:
        model = Family
        fields = [
            "first_name",
            "last_name",
            "id",
            "email",
            "phone_number",
            "num_children",
        ]

    def get_first_name(self, obj):
        return obj.parent.first_name

    def get_last_name(self, obj):
        return obj.parent.last_name

    def get_num_children(self, obj):
        return obj.children.count()


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
            "options",
            "order",
        ]
        list_serializer_class = FieldListSerializer

    def validate(self, attrs):
        request = self.context.get("request")
        if request.method == "POST":
            validate_field_order(attrs["order"], attrs["role"])
        return super().validate(attrs)
