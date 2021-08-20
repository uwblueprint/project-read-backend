from django.test import TestCase
from unittest.mock import patch

from registration.models import Family, Student, Field
from . import utils


class RegistrationUtilsTestCase(TestCase):
    def setUp(self):
        self.last_name = "Test"
        utils.create_test_fields()

    def test_create_test_fields(self):
        Field.objects.all().delete()
        utils.create_test_fields()
        self.assertEqual(Field.objects.all().count(), 13)

    def test_create_test_family(self):
        utils.create_test_family(last_name=self.last_name)
        self.assertEqual(Family.objects.all().count(), 1)
        self.assertEqual(
            Family.objects.all().first().email,
            "test@test.com",
        )

    def test_create_test_parent(self):
        family = utils.create_test_family(last_name=self.last_name)
        utils.create_test_parent(
            family=family,
            last_name=self.last_name,
        )
        self.assertEqual(Student.objects.all().count(), 1)

        parent = Student.objects.all().first()
        self.assertEqual(parent.role, Student.PARENT)
        self.assertEqual(parent.family, family)
        self.assertEqual(family.parent, parent)
        self.assertGreaterEqual(len(parent.information), 1)
        self.assertTrue(
            set([int(key) for key in parent.information.keys()]).issubset(
                Field.objects.filter(role=Student.PARENT).values_list("id", flat=True)
            )
        )

    def test_create_test_children(self):
        num_children = 3
        family = utils.create_test_family(last_name=self.last_name)
        utils.create_test_children(
            family=family,
            last_name=self.last_name,
            num_children=num_children,
        )
        self.assertEqual(Student.objects.all().count(), num_children)
        self.assertEqual(
            Student.objects.filter(
                family=family,
                last_name=self.last_name,
                role=Student.CHILD,
                date_of_birth__isnull=False,
            ).count(),
            num_children,
        )

        children = Student.objects.all()
        for child in children:
            self.assertGreaterEqual(len(child.information), 1)
            self.assertTrue(
                set([int(key) for key in child.information.keys()]).issubset(
                    Field.objects.filter(role=Student.CHILD).values_list(
                        "id", flat=True
                    )
                )
            )

    def test_create_test_guests(self):
        num_guests = 3
        family = utils.create_test_family(last_name=self.last_name)
        utils.create_test_guests(
            family=family,
            last_name=self.last_name,
            num_guests=num_guests,
        )
        self.assertEqual(Student.objects.all().count(), num_guests)
        self.assertEqual(
            Student.objects.filter(
                family=family, last_name=self.last_name, role=Student.GUEST
            ).count(),
            num_guests,
        )

        guests = Student.objects.all()
        for guest in guests:
            self.assertGreaterEqual(len(guest.information), 1)
            self.assertTrue(
                set([int(key) for key in guest.information.keys()]).issubset(
                    Field.objects.filter(role=Student.GUEST).values_list(
                        "id", flat=True
                    )
                )
            )

    @patch("registration.tests.utils.utils.create_test_guests")
    @patch("registration.tests.utils.utils.create_test_children")
    @patch("registration.tests.utils.utils.create_test_parent")
    @patch("registration.tests.utils.utils.create_test_family")
    def test_create_test_family_with_students(
        self,
        mock_family,
        mock_parent,
        mock_children,
        mock_guests,
    ):
        num_children = 3
        num_guests = 2

        utils.create_test_family_with_students(
            num_children=num_children,
            num_guests=num_guests,
        )

        mock_family.assert_called_once()
        last_name = mock_family.call_args.kwargs.get("last_name")

        mock_parent.assert_called_once_with(
            family=mock_family(),
            last_name=last_name,
        )
        mock_children.assert_called_once_with(
            family=mock_family(),
            last_name=last_name,
            num_children=num_children,
        )
        mock_guests.assert_called_once_with(
            family=mock_family(),
            last_name=last_name,
            num_guests=num_guests,
        )
