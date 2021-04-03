from django.core.exceptions import ValidationError
from django.test.testcases import TestCase
from unittest.mock import patch

from accounts.models import User
from registration.models import Student, Field
from registration.serializers import FieldSerializer, FieldListSerializer


class StudentSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        self.parent_field = Field.objects.create(
            role=Field.PARENT,
            name="email",
            question="What is your email?",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )
        self.other_parent_field = Field.objects.create(
            role=Field.PARENT,
            name="email",
            question="What is your email?",
            question_type=Field.TEXT,
            is_default=True,
            order=2,
        )
        self.child_field = Field.objects.create(
            role=Field.CHILD,
            name="Date Of Birth",
            question="When were you born?",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )
        self.guest_field = Field.objects.create(
            role=Field.GUEST,
            name="Relation to Family",
            question="How are you related?",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )

    def test_field_list_serializer(self):
        serializer = FieldListSerializer(child=FieldSerializer(), data=Field.objects)
        serializer.is_valid()
        self.assertEqual(
            serializer.data,
            [
                {
                    "parent_fields": [
                        FieldSerializer(self.parent_field).data,
                        FieldSerializer(self.other_parent_field).data,
                    ],
                    "child_fields": [FieldSerializer(self.child_field).data],
                    "guest_fields": [FieldSerializer(self.guest_field).data],
                }
            ],
        )

        # Test fields are sorted by order
        self.other_parent_field.order = 0
        self.other_parent_field.save()

        serializer = FieldListSerializer(child=FieldSerializer(), data=Field.objects)
        serializer.is_valid()
        self.assertEqual(
            serializer.data,
            [
                {
                    "parent_fields": [
                        FieldSerializer(self.other_parent_field).data,
                        FieldSerializer(self.parent_field).data,
                    ],
                    "child_fields": [FieldSerializer(self.child_field).data],
                    "guest_fields": [FieldSerializer(self.guest_field).data],
                }
            ],
        )
