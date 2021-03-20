from django.test.testcases import TestCase

from registration.models import Family, Student
from registration.serializers import FamilySerializer


class FamilySerializerTestCase(TestCase):
    def setUp(self):
        self.parent1 = Student.objects.create(
            first_name="Merlin", last_name="Fish", attendee_type=Student.PARENT
        )

        self.parent2 = Student.objects.create(
            first_name="Gandalf", last_name="Whale", attendee_type=Student.PARENT
        )

        self.family = Family.objects.create(
            parent=self.parent2,
            email="justkeepswimming@ocean.com",
            phone_number="123456789",
            address="1 Django Boulevard",
            preferred_comms="Shark Tune",
        )

        self.family_without_children = Family.objects.create(
            parent=self.parent1,
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

        self.child1 = Student.objects.create(
            first_name="Albus",
            last_name="Whale",
            attendee_type=Student.CHILD,
            family=self.family,
        )

        self.child2 = Student.objects.create(
            first_name="Lily",
            last_name="Whale",
            attendee_type=Student.CHILD,
            family=self.family,
        )

        self.child3 = Student.objects.create(
            first_name="Harry",
            last_name="Tuna",
            attendee_type=Student.CHILD,
            family=self.family_without_parent,
        )

    def test_family_serializer_parent_name(self):
        data = FamilySerializer(self.family_without_children).data
        self.assertEqual(data.get("first_name"), self.parent1.first_name)
        self.assertEqual(data.get("last_name"), self.parent1.last_name)

    def test_family_serializer_parent_name_none(self):
        data = FamilySerializer(self.family_without_parent).data
        self.assertEqual(data.get("first_name"), "")
        self.assertEqual(data.get("last_name"), "")

    def test_family_serializer_children(self):
        data = FamilySerializer(self.family).data
        self.assertEqual(data.get("num_children"), 2)

    def test_family_serializer_children_none(self):
        data = FamilySerializer(self.family_without_children).data
        self.assertEqual(data.get("num_children"), 0)
