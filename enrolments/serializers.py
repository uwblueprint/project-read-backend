from rest_framework import serializers
from registration.models import Family
from registration.serializers import StudentSerializer
from enrolments.models import Enrolment
from .models import Session, Class


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "season",
            "year",
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
        e_set = Enrolment.objects.filter(enrolled_class=obj)
        return [
            FamilyAttendanceSerializer(
                enrolment.family, read_only=True, context={"request": None}
            ).data
            for enrolment in e_set
            if enrolment.active == True
        ]
