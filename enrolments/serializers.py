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

    # def get_test():
    #     return self


class ClassListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "name", "facilitator_id"]


class ClassDetailSerializer(serializers.HyperlinkedModelSerializer):
    families = FamilyAttendanceSerializer(source='familyattendance_set', many=True, read_only=True)
    # source='stylecolor_set',
    #                               many=True, read_only=True
    # families = FamilyAttendanceSerializer.get_test
    # serializers.SerializerMethodField(method_name = )
    # families = serializers.HyperlinkedRelatedField(
    #     view_name="families-detail", read_only=True
    # )

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

# class ClassDetailSerializer(serializers.HyperlinkedModelSerializer):
#     families = FamilyAttendanceSerializer(many=True, read_only=True)

#     class Meta:
#         model = Enrolment
#         fields = [
#             "id",
#             "name",
#             "session_id",
#             "facilitator_id",
#             "attendance",
#             "families",
#         ]
