from django.test.testcases import TestCase

from registration.models import Family, Field, Student
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

        self.parent_data = {
            "first_name": "Molly",
            "last_name": "Weasley",
            "role": Student.PARENT,
            "date_of_birth": "2020-03-05",
            "information": {f"{self.parent_field.id}": "yes"},
        }
        self.parent = Student.objects.create(**self.parent_data)
        self.family_data = {
            "email": "weasleys@theorder.com",
            "home_number": "123456789",
            "cell_number": "144.618.8659x1124",
            "work_number": "793.373.9334",
            "preferred_number": "Work",
            "address": "12 Grimmauld Place",
            "preferred_comms": "Owl Post",
            "parent": self.parent,
            "notes": "Development perhaps successful they set.",
        }
        self.family = Family.objects.create(**self.family_data)
        self.parent.family = self.family

        self.children_data = [
            {
                "first_name": "Ron",
                "last_name": "Weasley",
                "family": self.family,
                "role": Student.CHILD,
                "date_of_birth": "2020-03-05",
                "information": {f"{self.child_field.id}": "male"},
            },
            {
                "first_name": "Ginny",
                "last_name": "Weasley",
                "family": self.family,
                "role": Student.CHILD,
                "date_of_birth": "2020-03-05",
                "information": {f"{self.child_field.id}": "female"},
            },
        ]
        self.guests_data = [
            {
                "first_name": "Harry",
                "last_name": "Potter",
                "family": self.family,
                "role": Student.GUEST,
                "date_of_birth": "2020-03-05",
                "information": {f"{self.guest_field.id}": "friend"},
            }
        ]

        child1 = Student.objects.create(**self.children_data[0])
        child2 = Student.objects.create(**self.children_data[1])
        guest = Student.objects.create(**self.guests_data[0])
        self.children_data[0]["id"] = child1.id
        self.children_data[1]["id"] = child2.id
        self.guests_data[0]["id"] = guest.id
        self.parent_data["id"] = self.parent.id
        self.child = child1

        self.family_data["children"] = self.children_data
        self.family_data["guests"] = self.guests_data
        self.family_data["parent"] = self.parent_data
        self.family_data["current_enrolment"] = None

    def test_family_detail_serializer_update(self):
        data = dict(self.family_data)
        data["email"] = "new_email"
        data["home_number"] = "new_home_number"
        data["preferred_comms"] = "Phone"

        serializer = FamilyDetailSerializer(instance=self.family, data=data)
        self.assertTrue(serializer.is_valid())
        family = serializer.save()

        self.assertEqual(family.email, data["email"])
        self.assertEqual(family.home_number, data["home_number"])
        self.assertEqual(family.preferred_comms, data["preferred_comms"])

    def test_family_detail_serializer_update_child(self):
        data = dict(self.family_data)
        new_name = "Pablo"
        data["children"][0]["first_name"] = new_name

        serializer = FamilyDetailSerializer(instance=self.family, data=data)
        self.assertTrue(serializer.is_valid())
        family = serializer.save()

        self.assertEqual(family.children.first().first_name, new_name)
        self.assertEqual(
            family.children.first().last_name, self.children_data[0]["last_name"]
        )
        self.assertEqual(
            family.children.first().date_of_birth.strftime(format="%Y-%m-%d"),
            self.children_data[0]["date_of_birth"],
        )
        self.assertEqual(
            family.children.first().information, self.children_data[0]["information"]
        )

    def test_family_detail_serializer_update__create_children(self):
        data = dict(self.family_data)
        new_child = {
            "id": None,
            "first_name": "Pableaux",
            "last_name": "Petersaune",
            "role": "Child",
            "date_of_birth": "2020-02-06",
            "family": self.family,
            "information": {},
        }
        data["children"].append(new_child)

        serializer = FamilyDetailSerializer(instance=self.family, data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(self.family.children.count(), 2)
        family = serializer.save()
        self.assertEqual(family.children.count(), 3)

        self.assertEqual(family.children[2].first_name, new_child["first_name"])
        self.assertEqual(family.children[2].last_name, new_child["last_name"])
        self.assertEqual(
            family.children[2].date_of_birth.strftime(format="%Y-%m-%d"),
            new_child["date_of_birth"],
        )
        self.assertEqual(family.children[2].information, new_child["information"])

    def test_family_detail_serializer_update__delete_children(self):
        data = dict(self.family_data)
        data["children"].pop(1)

        serializer = FamilyDetailSerializer(instance=self.family, data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(self.family.children.count(), 2)
        family = serializer.save()

        self.assertEqual(family.children.count(), 1)
        self.assertEqual(family.children.first(), self.child)

    def test_family_detail_serializer_update_read_only(self):  # should fail
        data = dict(self.family_data)
        old_child_role = data["children"][0]["role"]
        old_child_family = data["children"][0]["family"]
        data["children"][0]["role"] = "Guest"
        data["children"][0]["family"] = None

        serializer = FamilyDetailSerializer(instance=self.family, data=data)
        self.assertTrue(serializer.is_valid())
        family = serializer.save()

        self.assertEqual(family.children[0].role, old_child_role)
        self.assertEqual(family.children[0].family, old_child_family)
