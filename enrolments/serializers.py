from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from registration.models import Family
from accounts.models import User
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
            "colour",
            "days",
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
            "days",
        ]

    def get_families(self, obj):
        from registration.serializers import FamilySerializer

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
            for enrolment in obj.enrolments.filter(is_guest=False).order_by(
                "created_at"
            )
        ]


class ClassCreateSerializer(serializers.HyperlinkedModelSerializer):
    facilitator = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True
    )
    session = serializers.PrimaryKeyRelatedField(
        queryset=Session.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Class
        fields = [
            "id",
            "name",
            "session",
            "days",
            "location",
            "facilitator",
        ]

    def create(self, validated_data):
        class_obj = Class.objects.create(
            **validated_data, attendance=[{"date": "M&G", "attendees": []}]
        )
        class_obj.save()
        return class_obj


class SessionListSerializer(serializers.HyperlinkedModelSerializer):
    classes = ClassListSerializer(many=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "name",
            "classes",
            "active",
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
        from registration.serializers import FamilySerializer

        return [
            FamilySerializer(
                enrolment.family,
                context={
                    "request": self.context.get("request"),
                    "enrolment": EnrolmentSerializer(enrolment).data,
                },
            ).data
            for enrolment in obj.enrolments.filter(is_guest=False).order_by(
                "created_at"
            )
        ]


class SessionCreateSerializer(serializers.ModelSerializer):
    classes = ClassCreateSerializer(many=True)

    class Meta:
        model = Session
        fields = [
            "name",
            "start_date",
            "fields",
            "classes",
        ]

    def create(self, validated_data):
        classes = validated_data.pop("classes")
        session = Session.objects.create(**validated_data)
        for class_obj in classes:
            Class.objects.create(session=session, **class_obj)

        return session


class EnrolmentSerializer(serializers.HyperlinkedModelSerializer):
    family = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        queryset=Family.objects.all(),
    )
    session = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all())
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
            "enrolled_class",
            "family",
            "preferred_class",
            "session",
            "status",
            "students",
            "created_at",
        ]
        read_only_fields = [
            "created_at",
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
        if self.instance is not None:
            # updates should validate against the existing family & session
            if attrs["family"] != self.instance.family:
                raise serializers.ValidationError("family cannot be updated")
            if attrs["session"] != self.instance.session:
                raise serializers.ValidationError("session cannot be updated")

            validate_student_ids_in_family(attrs["students"], self.instance.family)
            validate_class_in_session(attrs["preferred_class"], self.instance.session)
            validate_class_in_session(attrs["enrolled_class"], self.instance.session)

        else:
            # creates should validate against the provided family & session
            validate_student_ids_in_family(attrs["students"], attrs["family"])
            validate_class_in_session(attrs["preferred_class"], attrs["session"])
            validate_class_in_session(attrs["enrolled_class"], attrs["session"])

        return super().validate(attrs)
