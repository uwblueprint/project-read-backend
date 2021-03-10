from rest_framework.test import APITestCase

from registration.models import Family, Student
from registration.serializers import FamilySerializer


class SerializersTestCase(APITestCase):
    def setUp(self):
        self.parent = Student.objects.create(
            first_name="Merlin", last_name="Fish", attendee_type="Parent"
        )
        self.family = Family.objects.create(
            parent=self.parent,
            email="justkeepswimming@ocean.com",
            phone_number="123456789",
            address="42 Wallaby Way",
            preferred_comms="Whale Song",
        )
        self.family_without_parent = Family.objects.create(
            email="justkeepswimming@ocean.com",
            phone_number="123456789",
            address="1 Test Ave",
            preferred_comms="Dolphin Whistle",
        )

    def test_family_serializer_parent_name(self):
        data = FamilySerializer(self.family).data
        self.assertEqual(data.get("first_name"), self.parent.first_name)
        self.assertEqual(data.get("last_name"), self.parent.last_name)

    def test_family_serializer_parent_name_none(self):
        data = FamilySerializer(self.family_without_parent).data
        self.assertEqual(data.get("first_name"), "")
        self.assertEqual(data.get("last_name"), "")
