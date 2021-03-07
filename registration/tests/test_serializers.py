from rest_framework.test import APITestCase

from registration.models import Family, Student, FamilyInfo
from registration.serializers import FamilySerializer, FamilyDetailSerializer


class SerializersTestCase(APITestCase):
    def setUp(self):
        self.parent_field = FamilyInfo.objects.create(
            name="Internet Access", question="Do you have access to internet?"
        )
        self.other_parent_field = FamilyInfo.objects.create(
            name="Allergies", question="Do you have any allergies?"
        )
        self.parent_field_response = "Yes"
        self.other_parent_field_response = "Sharks"
        self.parent = Student.objects.create(
            first_name="Merlin",
            last_name="Fish",
            attendee_type=Student.PARENT,
            information=[
                {"id": self.parent_field.id, "response": self.parent_field_response},
                {
                    "id": self.other_parent_field.id,
                    "response": self.other_parent_field_response,
                },
            ],
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

    def test_family_detail_serializer(self):
        data = FamilyDetailSerializer(self.family).data
        self.assertEqual(
            data,
            {
                "id": self.family.id,
                "first_name": self.parent.first_name,
                "last_name": self.parent.last_name,
                "email": self.family.email,
                "phone_number": self.family.phone_number,
                "address": self.family.address,
                "preferred_comms": self.family.preferred_comms,
                self.parent_field.name: self.parent_field_response,
                self.other_parent_field.name: self.other_parent_field_response,
            },
        )

    def test_family_detail_serializer_no_parent(self):
        data = FamilyDetailSerializer(self.family_without_parent).data
        self.assertEqual(
            data,
            {
                "id": self.family_without_parent.id,
                "first_name": "",
                "last_name": "",
                "email": self.family_without_parent.email,
                "phone_number": self.family_without_parent.phone_number,
                "address": self.family_without_parent.address,
                "preferred_comms": self.family_without_parent.preferred_comms,
            },
        )
