from rest_framework import serializers
from registration.models import Family
from registration.serializers import StudentSerializer


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
