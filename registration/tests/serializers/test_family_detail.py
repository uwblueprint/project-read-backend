from django.test.testcases import TestCase

from registration.models import Family, Student
from registration.serializers import FamilyDetailSerializer, StudentSerializer

context = {"request": None}


class FamilyDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.family = Family.objects.create(
            email="closets@pritchett.com",
            phone_number="123456789",
            address="10 Modern Lane",
            preferred_comms="Phone",
        )
        self.parent = Student.objects.create(
            first_name="Claire",
            last_name="Dunphy",
            role=Student.PARENT,
            family=self.family,
        )
        self.family.parent = self.parent
        self.family.parent.save()
        self.child = Student.objects.create(
            first_name="Haley",
            last_name="Dunphy",
            role=Student.CHILD,
            family=self.family,
        )
        self.guest = Student.objects.create(
            first_name="Phil",
            last_name="Dunphy",
            role=Student.GUEST,
            family=self.family,
        )

        self.post_data = {
            "email": "weasleys@theorder.com",
            "phone_number": "123456789",
            "address": "12 Grimmauld Place",
            "preferred_comms": "Owl Post",
            "parent": {
                "first_name": "Molly",
                "last_name": "Weasley",
                "information": {"2": "yes"},
            },
            "children": [
                {
                    "first_name": "Ron",
                    "last_name": "Weasley",
                    "information": {"1": "male"},
                },
                {
                    "first_name": "Ginny",
                    "last_name": "Weasley",
                    "information": {"1": "female"},
                },
            ],
            "guests": [
                {
                    "first_name": "Harry",
                    "last_name": "Potter",
                    "information": {"3": "friend"},
                }
            ],
        }

    def test_family_detail_serializer_parent(self):
        data = FamilyDetailSerializer(self.family, context=context).data
        self.assertEqual(
            data["parent"], StudentSerializer(self.parent, context=context).data
        )

    def test_family_detail_serializer_children(self):
        data = FamilyDetailSerializer(self.family, context=context).data
        self.assertEqual(
            data["children"], [StudentSerializer(self.child, context=context).data]
        )

    def test_family_detail_serializer_guests(self):
        data = FamilyDetailSerializer(self.family, context=context).data
        self.assertEqual(
            data["guests"], [StudentSerializer(self.guest, context=context).data]
        )

    def test_family_detail_serializer_create(self):
        num_families = Family.objects.all().count()
        num_students = Student.objects.all().count()

        data = self.post_data

        serializer = FamilyDetailSerializer(data=data)
        serializer.is_valid()
        family = serializer.save()

        self.assertEqual(Family.objects.all().count(), num_families + 1)
        self.assertEqual(Student.objects.all().count(), num_students + 4)

        self.assertEqual(family.parent.first_name, data["parent"]["first_name"])
        self.assertEqual(family.parent.last_name, data["parent"]["last_name"])
        self.assertEqual(family.parent.information, data["parent"]["information"])

        self.assertEqual(family.children.count(), 2)

        child1 = family.children.get(first_name=data["children"][0]["first_name"])
        self.assertEqual(child1.last_name, data["children"][0]["last_name"])
        self.assertEqual(child1.information, data["children"][0]["information"])

        child2 = family.children.get(first_name=data["children"][1]["first_name"])
        self.assertEqual(child2.last_name, data["children"][1]["last_name"])
        self.assertEqual(child2.information, data["children"][1]["information"])

        self.assertEqual(family.guests.count(), 1)
        guest = family.guests.first()
        self.assertEqual(guest.first_name, data["guests"][0]["first_name"])
        self.assertEqual(guest.last_name, data["guests"][0]["last_name"])
        self.assertEqual(guest.information, data["guests"][0]["information"])

    def test_family_detail_serializer_create_invalid(self):
        # missing family field
        data = dict(self.post_data).pop("email")
        self.assertFalse(FamilyDetailSerializer(data=data).is_valid())

        # missing student field
        data = dict(self.post_data)["parent"].pop("first_name")
        self.assertFalse(FamilyDetailSerializer(data=data).is_valid())

        # no parent
        data = dict(self.post_data).pop("parent")
        self.assertFalse(FamilyDetailSerializer(data=data).is_valid())

        # no children
        data = dict(self.post_data).pop("children")
        self.assertFalse(FamilyDetailSerializer(data=data).is_valid())

        # no guests
        data = dict(self.post_data).pop("guests")
        self.assertFalse(FamilyDetailSerializer(data=data).is_valid())
