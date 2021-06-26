from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from registration.models import Family
from registration.serializers import FamilySerializer, StudentSerializer
from .models import Session, Class, Enrolment


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "season",
            "year",
        ]


class SessionDetailSerializer(serializers.HyperlinkedModelSerializer):
    families = SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            "id",
            "season",
            "year",
            "families",
            "fields",
        ]

    def get_families(self, obj):
        return [
            FamilySerializer(enrolment.family, context={"request": None}).data
            for enrolment in obj.enrolments.filter(active=True)
        ]


class FamilyAttendanceSerializer(serializers.HyperlinkedModelSerializer):
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Family
        fields = [
            "id",
            "email",
            "phone_number",
            "students",
        ]


class ClassListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "name", "facilitator_id"]


class ClassDetailSerializer(serializers.HyperlinkedModelSerializer):
    families = serializers.SerializerMethodField()  # defaults to get_families

    class Meta:
        model = Class
        fields = [
            "id",
            "name",
            "session_id",
            "facilitator_id",
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
