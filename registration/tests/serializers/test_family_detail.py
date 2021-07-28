from django.test.testcases import TestCase

from accounts.serializers import UserSerializer
from registration.models import Family, Student
from accounts.models import User
from registration.serializers import FamilyDetailSerializer, StudentSerializer

context = {"request": None}


class FamilyDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="user@test.com",
            first_name="Stella",
            last_name="Pritchett",
        )
        self.family = Family.objects.create(
            email="closets@pritchett.com",
            cell_number="123456789",
            preferred_number="Cell",
            address="10 Modern Lane",
            preferred_comms="Phone",
            interactions=[
                {
                    "type": "Phone Call",
                    "date": "2012-04-04",
                    "user_id": self.user.id,
                }
            ],
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

    def test_family_detail_serializer_interactions(self):
        data = FamilyDetailSerializer(self.family, context=context).data
        self.assertEqual(
            data["interactions"],
            [
                {
                    "type": "Phone Call",
                    "date": "2012-04-04",
                    "user": UserSerializer(self.user).data,
                }
            ],
        )
