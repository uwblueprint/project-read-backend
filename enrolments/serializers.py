from django.db.models import query
from rest_framework import response, serializers
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
    session = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all())
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
        read_only_fields = ["session"]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["session"] = SessionListSerializer(instance.session).data
        response["preferred_class"] = ClassListSerializer(instance.preferred_class).data
        response["enrolled_class"] = ClassListSerializer(instance.enrolled_class).data
        return response

    def validate(self, attrs):
        class_ids = set()
        if not attrs["preferred_class"] == None:
            class_ids.add(attrs["preferred_class"].id)
        if not attrs["enrolled_class"] == None:
            class_ids.add(attrs["enrolled_class"].id)
        if (
            len(class_ids)
            != Class.objects.filter(
                id__in=list(class_ids), session=attrs["session"].id
            ).count()
        ):
            raise serializers.ValidationError("Classes do not exist in Session")
        return super().validate(attrs)
