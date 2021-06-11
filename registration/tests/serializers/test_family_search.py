from django.test.testcases import TestCase

from registration.models import Family, Student
from registration.serializers import FamilySearchSerializer

context = {"request": None}


class FamilyDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.family = Family.objects.create(
            email="closets@pritchett.com",
            cell_number="123456789",
            preferred_number="Cell",
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

    def test_family_search_serializer_parent_fields(self):
        data = FamilySearchSerializer(self.family, context=context).data
        self.assertEqual(data["first_name"], self.parent.first_name)
        self.assertEqual(data["last_name"], self.parent.last_name)

    def test_family_search_serializer_num_children(self):
        data = FamilySearchSerializer(self.family, context=context).data
        self.assertEqual(data["num_children"], 1)
