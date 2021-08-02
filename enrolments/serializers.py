from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from registration.models import Student
from registration.serializers import (
    FamilyDetailSerializer,
    FamilySerializer,
)
from .models import Session, Class, Enrolment
from .validators import (
    validate_class_in_session,
    validate_student_ids_in_family,
)


class ClassListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Class
        fields = [
            "id",
            "name",
        ]


class SessionListSerializer(serializers.HyperlinkedModelSerializer):
    classes = ClassListSerializer(many=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "name",
            "classes",
        ]


class SessionDetailSerializer(serializers.HyperlinkedModelSerializer):
    classes = ClassListSerializer(many=True)
    families = SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            "id",
            "name",
            "families",
            "fields",
            "classes",
        ]

    def get_families(self, obj):
        return [
            FamilySerializer(
                enrolment.family,
                context={
                    "request": self.context.get("request"),
                    "enrolment": EnrolmentSerializer(enrolment).data,
                },
            ).data
            for enrolment in obj.enrolments.filter(active=True)
        ]


class ClassDetailSerializer(serializers.HyperlinkedModelSerializer):
    families = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = [
            "id",
            "name",
            "attendance",
            "families",
        ]

    def get_families(self, obj):
        request = self.context.get("request")
        return [
            FamilySerializer(
                enrolment.family,
                context={
                    "request": request,
                    "enrolment": EnrolmentSerializer(
                        enrolment, context={"request": request}
                    ).data,
                },
            ).data
            for enrolment in obj.enrolments.filter(active=True)
        ]


class EnrolmentSerializer(serializers.HyperlinkedModelSerializer):
    session = serializers.PrimaryKeyRelatedField(read_only=True)
    preferred_class = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(), allow_null=True
    )
    enrolled_class = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(), allow_null=True
    )

    class Meta:
        model = Enrolment
        fields = [
            "id",
            "session",
            "preferred_class",
            "enrolled_class",
            "status",
            "students",
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["session"] = SessionListSerializer(instance.session).data
        if response["preferred_class"] is not None:
            response["preferred_class"] = ClassListSerializer(
                instance.preferred_class
            ).data
        if response["enrolled_class"] is not None:
            response["enrolled_class"] = ClassListSerializer(
                instance.enrolled_class
            ).data
        return response

    def validate(self, attrs):
        try:
            validate_student_ids_in_family(attrs["students"], self.instance.family)
            validate_class_in_session(attrs["preferred_class"], self.instance.session)
            validate_class_in_session(attrs["enrolled_class"], self.instance.session)
        except ValidationError:
            raise serializers.ValidationError(ValidationError)

        return super().validate(attrs)


class EnrolmentCreateSerializer(serializers.ModelSerializer):
    family = FamilyDetailSerializer()
    preferred_class = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Class.objects.all()
    )
    session = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all())

    class Meta:
        model = Enrolment
        fields = [
            "family",
            "session",
            "preferred_class",
            "status",
        ]

    def create(self, validated_data):
        family = FamilyDetailSerializer.create(None, validated_data["family"])
        students = family.students.all()

        enrolments = Enrolment.objects.create(
            active=True,
            family=family,
            students=[student.id for student in students],
            session=validated_data["session"],
            preferred_class=validated_data["preferred_class"],
            status=validated_data["status"],
        )

        return enrolments

    def validate(self, attrs):
        try:
            if attrs["preferred_class"]:
                validate_class_in_session(attrs["preferred_class"], attrs["session"])
        except:
            raise serializers.ValidationError(
                detail="preferred class does not exist in session",
                code="invalid_preferred_class",
            )

        return super().validate(attrs)
