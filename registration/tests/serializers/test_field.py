from django.test.testcases import TestCase

from accounts.models import User
from registration.models import Field
from registration.serializers import FieldSerializer, FieldListSerializer


class FieldSerializerTestCase(TestCase):
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
        self.session_field = Field.objects.create(
            role=Field.SESSION,
            name="Time Lived in Canada",
            question="How long have you been in Canada?",
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
                    "session_fields": [FieldSerializer(self.session_field).data],
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
                    "session_fields": [FieldSerializer(self.session_field).data],
                }
            ],
        )

    def test_field_serializer__order_validator(self):
        field_request_invalid_order = {
            "role": Field.PARENT,
            "name": "Favourite Colour",
            "question": "What is your favourite colour?",
            "question_type": "Text",
            "is_default": False,
            "options": [],
            "order": 1,
        }

        serializer = FieldSerializer(data=field_request_invalid_order)
        self.assertFalse(serializer.is_valid())

        field_request_invalid_order["order"] = 4
        serializer = FieldSerializer(data=field_request_invalid_order)
        self.assertFalse(serializer.is_valid())

        field_request_invalid_order["order"] = 3
        serializer = FieldSerializer(data=field_request_invalid_order)
        self.assertTrue(serializer.is_valid())
