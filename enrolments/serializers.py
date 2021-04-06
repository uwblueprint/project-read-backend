from rest_framework import serializers
from registration.models import Family
from registration.serializers import StudentSerializer
from .models import Session, Class, Enrolment


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
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = [
            "id",
            "email",
            "phone_number",
            "students",
        ]

    def get_phone_number(self, obj):
        if obj.preferred_number == "Cell":
            return obj.cell_number
        elif obj.preferred_number == "Home":
            return obj.home_number
        elif obj.preferred_number == "Work":
            return obj.work_number


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
            FamilyAttendanceSerializer(
                enrolment.family, read_only=True, context={"request": None}
            ).data
            for enrolment in e_set
        ]
