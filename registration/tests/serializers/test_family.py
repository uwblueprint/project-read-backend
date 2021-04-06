from django.test.testcases import TestCase

from registration.models import Family, Student
from registration.serializers import FamilySerializer, StudentSerializer


class FamilySerializerTestCase(TestCase):
    def setUp(self):
        self.parent1 = Student.objects.create(
            first_name="Merlin", last_name="Fish", role=Student.PARENT
        )

        self.parent2 = Student.objects.create(
            first_name="Gandalf", last_name="Whale", role=Student.PARENT
        )

        self.family = Family.objects.create(
            parent=self.parent2,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            home_number="1111111111",
            preferred_number="Home",
            address="1 Django Boulevard",
            preferred_comms="Shark Tune",
        )

        self.family_without_children = Family.objects.create(
            parent=self.parent1,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            address="42 Wallaby Way",
            preferred_comms="Whale Song",
        )

        self.family_without_parent = Family.objects.create(
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            address="1 Test Ave",
            preferred_comms="Dolphin Whistle",
        )

        self.child1 = Student.objects.create(
            first_name="Albus",
            last_name="Whale",
            role=Student.CHILD,
            family=self.family,
        )

        self.child2 = Student.objects.create(
            first_name="Lily",
            last_name="Whale",
            role=Student.CHILD,
            family=self.family,
        )

        self.child3 = Student.objects.create(
            first_name="Harry",
            last_name="Tuna",
            role=Student.CHILD,
            family=self.family_without_parent,
        )

    def test_family_number(self):
        self.maxDiff = None
        self.assertDictEqual(
            {
                "id": self.family.id,
                "parent": StudentSerializer(
                    self.family.parent, context={"request": None}
                ).data,
                "email": self.family.email,
                "phone_number": self.family.home_number,
                "address": self.family.address,
                "preferred_comms": self.family.preferred_comms,
                "num_children": 2,
            },
            FamilySerializer(self.family, context={"request": None}).data,
        )

    def test_family_serializer_parent(self):
        data = FamilySerializer(self.family_without_children).data
        self.assertEqual(data["parent"], StudentSerializer(self.parent1).data)
        self.assertEqual(data["parent"], StudentSerializer(self.parent1).data)

    def test_family_serializer_children(self):
        data = FamilySerializer(self.family).data
        self.assertEqual(data.get("num_children"), 2)

    def test_family_serializer_children_none(self):
        data = FamilySerializer(self.family_without_children).data
        self.assertEqual(data.get("num_children"), 0)
