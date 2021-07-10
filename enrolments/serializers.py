from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from registration.models import Family
from registration.serializers import (
    FamilyDetailSerializer,
    FamilySerializer,
    StudentSerializer,
)
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
    session = SessionListSerializer()
    preferred_class = ClassListSerializer()
    enrolled_class = ClassListSerializer()

    class Meta:
        model = Enrolment
        fields = [
            "id",
            "session",
            "preferred_class",
            "enrolled_class",
            "status",
        ]


class EnrolmentCreateSerializer(serializers.ModelSerializer):
    # session = SessionListSerializer()
    # preferred_class = ClassListSerializer()
    # enrolled_class = ClassListSerializer()
    family = FamilyDetailSerializer()

    class Meta:
        model = Enrolment
        fields = [
            "family",
            "session",
            "preferred_class",
        ]

    def create(self, validated_data):
        session = validated_data["session"]
        preferred_class = validated_data["preferred_class"]

        family_data = dict(validated_data["family"])
        family_serializer = FamilyDetailSerializer(data=family_data)
        family = family_serializer.save()

        enrolments = Enrolment.objects.create(
            active=True,
            family_id=family.id,
            session=session.id,
            preferred_class=preferred_class.id,
        )

        return enrolments

    def validate(self, attrs):
        family_data = dict(attrs["family"])
        family_serializer = FamilyDetailSerializer(data=family_data)
        if not (family_serializer.is_valid()):
            raise serializers.ValidationError("Family data is invalid")
        return super().validate(attrs)
