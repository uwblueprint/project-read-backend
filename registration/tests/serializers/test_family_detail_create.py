from django.core.exceptions import ValidationError
from django.test.testcases import TestCase
from unittest.mock import patch

from registration.models import Family, Student, Field
from registration.serializers import FamilyDetailSerializer


class FamilyDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.parent_field = Field.objects.create(
            role=Field.PARENT,
            name="Internet Access",
            question="Do you have access to internet",
            question_type=Field.TEXT,
            is_default=True,
            order=1,
        )
        self.child_field = Field.objects.create(
            role=Field.CHILD,
            name="Gender",
            question="What is their gender?",
            question_type=Field.MULTIPLE_CHOICE,
            is_default=True,
            order=1,
        )
        self.guest_field = Field.objects.create(
            role=Field.GUEST,
            name="Relationship",
            question="What's their relationship to your family?",
            question_type=Field.MULTIPLE_CHOICE,
            is_default=True,
            order=1,
        )

        self.family_data = {
            "email": "weasleys@theorder.com",
            "phone_number": "123456789",
            "address": "12 Grimmauld Place",
            "preferred_comms": "Owl Post",
        }
        self.parent_data = {
            "first_name": "Molly",
            "last_name": "Weasley",
            "information": {f"{self.parent_field.id}": "yes"},
        }
        self.children_data = [
            {
                "first_name": "Ron",
                "last_name": "Weasley",
                "information": {f"{self.child_field.id}": "male"},
            },
            {
                "first_name": "Ginny",
                "last_name": "Weasley",
                "information": {f"{self.child_field.id}": "female"},
            },
        ]
        self.guests_data = [
            {
                "first_name": "Harry",
                "last_name": "Potter",
                "information": {f"{self.guest_field.id}": "friend"},
            }
        ]

    def test_family_detail_serializer_create(self):
        num_families = Family.objects.all().count()
        num_students = Student.objects.all().count()

        data = dict(self.family_data)
        data["parent"] = self.parent_data

        serializer = FamilyDetailSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        family = serializer.save()

        self.assertEqual(Family.objects.all().count(), num_families + 1)
        self.assertEqual(Student.objects.all().count(), num_students + 1)

        self.assertEqual(family.parent.first_name, self.parent_data["first_name"])
        self.assertEqual(family.parent.last_name, self.parent_data["last_name"])
        self.assertEqual(family.parent.information, self.parent_data["information"])

    def test_family_detail_serializer_create__children_guests(self):
        num_families = Family.objects.all().count()
        num_students = Student.objects.all().count()

        data = dict(self.family_data)
        data["parent"] = self.parent_data
        data["children"] = self.children_data
        data["guests"] = self.guests_data

        serializer = FamilyDetailSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        family = serializer.save()

        self.assertEqual(Family.objects.all().count(), num_families + 1)
        self.assertEqual(Student.objects.all().count(), num_students + 4)

        self.assertEqual(family.parent.first_name, self.parent_data["first_name"])
        self.assertEqual(family.parent.last_name, self.parent_data["last_name"])
        self.assertEqual(family.parent.information, self.parent_data["information"])

        self.assertEqual(family.children.count(), 2)

        child1 = family.children.get(first_name=self.children_data[0]["first_name"])
        self.assertEqual(child1.last_name, self.children_data[0]["last_name"])
        self.assertEqual(child1.information, self.children_data[0]["information"])

        child2 = family.children.get(first_name=self.children_data[1]["first_name"])
        self.assertEqual(child2.last_name, self.children_data[1]["last_name"])
        self.assertEqual(child2.information, self.children_data[1]["information"])

        self.assertEqual(family.guests.count(), 1)
        guest = family.guests.first()
        self.assertEqual(guest.first_name, self.guests_data[0]["first_name"])
        self.assertEqual(guest.last_name, self.guests_data[0]["last_name"])
        self.assertEqual(guest.information, self.guests_data[0]["information"])

    def test_family_detail_serializer_validate__no_parent(self):
        data = dict(self.family_data)
        self.assertFalse(FamilyDetailSerializer(data=data).is_valid())

    @patch(
        "registration.serializers.validate_student_information",
    )
    def test_family_detail_serializer_validate(self, mock_validate):
        data = dict(self.family_data)
        data["parent"] = self.parent_data
        data["children"] = self.children_data
        data["guests"] = self.guests_data

        is_valid = FamilyDetailSerializer(data=data).is_valid()
        mock_validate.assert_called_once_with(
            [self.parent_data] + self.children_data + self.guests_data
        )
        self.assertTrue(is_valid)

    @patch(
        "registration.serializers.validate_student_information",
        side_effect=ValidationError(""),
    )
    def test_family_detail_serializer_validate__invalid(self, mock_validate):
        data = dict(self.family_data)
        data["parent"] = self.parent_data
        data["children"] = self.children_data
        data["guests"] = self.guests_data

        is_valid = FamilyDetailSerializer(data=data).is_valid()
        mock_validate.assert_called_once_with(
            [self.parent_data] + self.children_data + self.guests_data
        )
        self.assertFalse(is_valid)
