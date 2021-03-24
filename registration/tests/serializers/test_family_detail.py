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
