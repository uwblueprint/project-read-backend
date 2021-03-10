from rest_framework import serializers
from .models import Family, Student, FamilyInfo, ChildInfo


class FamilySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Family
        fields = [
            "id",
            "email",
            "phone_number",
            "address",
            "preferred_comms",
        ]


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    family = serializers.HyperlinkedRelatedField(
        view_name="families-detail", read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "attendee_type",
            "family",
            "information",
        ]


class ChildInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChildInfo
        fields = [
            "id",
            "name",
            "question",
            "active",
        ]
