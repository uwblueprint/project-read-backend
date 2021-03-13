from rest_framework import serializers
from registration.models import Family
from registration.serializers import StudentSerializer
from .models import Session, Class

from rest_framework.response import Response

class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "season",
            "year",
        ]


class FamilyAttendanceSerializer(serializers.HyperlinkedModelSerializer):
    # students = StudentSerializer(many=True, read_only=True)
    students = Response(StudentSerializer(many=True, read_only=True).data)
    # students = serializers.HyperlinkedRelatedField(
    #     view_name="students-detail", read_only=True
    # )
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
