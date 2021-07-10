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
    session = SessionListSerializer(read_only=True)
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

    def update(self, instance, validated_data):
        instance.preferred_class = Class.objects.get(
            id=validated_data.pop("preferred_class_id"), session=instance.session
        )
        instance.enrolled_class = Class.objects.get(
            id=validated_data.pop("enrolled_class_id"), session=instance.session
        )
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        return instance

    def to_internal_value(self, data):
        data["preferred_class_id"] = data.pop("preferred_class", {})["id"]
        data["enrolled_class_id"] = data.pop("enrolled_class", {})["id"]
        return data

    def validate(self, attrs):
        class_ids = {attrs["preferred_class_id"], attrs["enrolled_class_id"]}
        if (
            len(class_ids)
            != Class.objects.filter(
                id__in=list(class_ids), session=attrs["session"]["id"]
            ).count()
        ):
            raise serializers.ValidationError("Classes do not exist in Session")
        return super().validate(attrs)
