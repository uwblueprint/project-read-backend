from rest_framework.test import APITestCase

from registration.models import Family, Student, FamilyInfo
from registration.serializers import FamilySerializer, FamilyDetailSerializer


class SerializersTestCase(APITestCase):
    def setUp(self):
        self.parent_field = FamilyInfo.objects.create(
            name="Internet Access", question="Do you have access to internet?"
        )
        self.parent = Student.objects.create(
            first_name="Merlin",
            last_name="Fish",
            attendee_type="Parent",
            information=[{"id": self.parent_field.id, "response": "Yes"}],
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

    def test_family_detail_serializer_parent_name(self):
        data = FamilyDetailSerializer(self.family).data
        self.assertEqual(data.get("first_name"), self.parent.first_name)
        self.assertEqual(data.get("last_name"), self.parent.last_name)

    def test_family_detail_serializer_parent_name_none(self):
        data = FamilyDetailSerializer(self.family_without_parent).data
        self.assertEqual(data.get("first_name"), "")
        self.assertEqual(data.get("last_name"), "")

    def test_family_detail_serializer_parent_information(self):
        data = FamilyDetailSerializer(self.family).data
        self.assertEqual(data.get("parent_fields"), self.parent.information)

    def test_family_detail_serializer_parent_information_none(self):
        data = FamilyDetailSerializer(self.family_without_parent).data
        self.assertEqual(data.get("parent_fields"), {})
