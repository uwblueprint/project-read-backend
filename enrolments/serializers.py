from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from registration.serializers import FamilySerializer
from .models import Session, Class, Enrolment


class SessionListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "season",
            "year",
        ]


class ClassListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "name"]


class SessionDetailSerializer(serializers.HyperlinkedModelSerializer):
    classes = ClassListSerializer(many=True)
    families = SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            "id",
            "season",
            "year",
            "families",
            "fields",
            "classes",
        ]

    def get_families(self, obj):
        return [
            FamilySerializer(enrolment.family, context={"request": None}).data
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
        e_set = Enrolment.objects.filter(enrolled_class=obj, active=True)
        return [
            FamilySerializer(
                enrolment.family, read_only=True, context={"request": None}
            ).data
            for enrolment in e_set
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
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["session"] = SessionListSerializer(instance.session).data
        response["preferred_class"] = ClassListSerializer(instance.preferred_class).data
        response["enrolled_class"] = ClassListSerializer(instance.enrolled_class).data
        return response

    def validate(self, attrs):
        if (
            attrs["preferred_class"] is not None
            and attrs["preferred_class"].session != self.instance.session
        ):
            raise serializers.ValidationError(
                "Perferred class does not exist in Session"
            )
        if (
            attrs["enrolled_class"] is not None
            and attrs["enrolled_class"].session != self.instance.session
        ):
            raise serializers.ValidationError(
                "Enrolled class does not exist in Session"
            )
        return super().validate(attrs)
