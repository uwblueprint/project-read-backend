from django.db import models, transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Family, Student, Field
from .validators import validate_student_information_role
from enrolments.models import Enrolment
from accounts.models import User
from accounts.serializers import UserSerializer


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
        # read_only_fields = ["role", "family"]

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
            "enrolment",
        ]

    def get_num_children(self, obj):
        return obj.children.count()

    def get_enrolment(self, obj):
        enrolment = self.context.get("enrolment")
        if enrolment is not None:
            return enrolment

        if obj.current_enrolment is not None:
            from enrolments.serializers import EnrolmentSerializer

            return EnrolmentSerializer(obj.current_enrolment).data

        return None


class FamilyDetailSerializer(serializers.HyperlinkedModelSerializer):
    parent = StudentSerializer()
    children = StudentSerializer(many=True)
    guests = StudentSerializer(many=True)
    current_enrolment = SerializerMethodField()
    interactions = serializers.SerializerMethodField()

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
            "current_enrolment",
            "interactions",
        ]
        read_only_fields = ["interactions"]

    def get_current_enrolment(self, obj):
        from enrolments.serializers import EnrolmentSerializer

        if obj.current_enrolment is None:
            return None
        return EnrolmentSerializer(obj.current_enrolment).data

    def get_interactions(self, obj):
        interactions = obj.interactions
        for interaction in interactions:
            user = User.objects.get(id=interaction.pop("user_id"))
            interaction["user"] = UserSerializer(user).data
        return interactions

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
        students_data = validated_data.pop("students")
        students = (
            [instance.parent]
            + list(instance.children.all())
            + list(instance.guests.all())
        )

        instance.email = validated_data.get("email", instance.email)
        instance.home_number = validated_data.get("home_number", instance.home_number)
        instance.cell_number = validated_data.get("cell_number", instance.cell_number)
        instance.work_number = validated_data.get("work_number", instance.work_number)
        instance.preferred_number = validated_data.get(
            "preferred_number", instance.preferred_number
        )
        instance.address = validated_data.get("address", instance.address)
        instance.preferred_comms = validated_data.get(
            "preferred_comms", instance.preferred_comms
        )
        instance.notes = validated_data.get("notes", instance.notes)

        student_objs = Student.objects.filter(id__in=[student.id for student in students])
        student_data_objs = Student.objects.filter(id__in=[student["id"] for student in students_data])

        if(len(student_objs) > len(student_data_objs)):
            student_to_delete = student_objs.difference(student_data_objs)
            student_to_delete.delete()

        if(len(student_objs) < len(student_data_objs)):
            student_to_create = student_objs.difference(student_data_objs)
            student_to_create.create()
            

        intersection_of_students = student_objs.intersection(student_data_objs)
        for student, intersection_of_students in zip(students, intersection_of_students):
            student.first_name = intersection_of_students.first_name
            student.last_name = intersection_of_students.last_name
            student.date_of_birth = intersection_of_students.date_of_birth
            student.information = intersection_of_students.information
            student.save()

        instance.save()
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
