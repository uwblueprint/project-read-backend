from registration.models import Field
from django.test import TestCase

from enrolments.models import Session, Class, Enrolment
from .utils import create_test_sessions, create_test_classes, create_test_enrolments
from registration.tests.utils.utils import create_test_family_with_students


class EnrolmentUtilsTestCase(TestCase):
    def test_create_test_sessions(self):
        num_sessions = 10
        create_test_sessions(num_sessions=num_sessions)
        self.assertEqual(
            Session.objects.all().count(),
            num_sessions,
        )
        self.assertEqual(
            Session.objects.filter(fields__len=0).count(),
            num_sessions,
        )

    def test_create_test_sessions__with_fields(self):
        field = Field.objects.create(is_default=True, order=1)
        num_sessions = 10
        create_test_sessions(num_sessions=num_sessions, fields=[1])
        self.assertEqual(
            Session.objects.filter(fields__contains=[1]).count(),
            num_sessions,
        )

    def test_create_test_classes(self):
        num_classes = 10
        session = create_test_sessions(num_sessions=1)[0]
        create_test_classes(session=session, num_classes=num_classes)
        self.assertEqual(
            Session.objects.all().count(),
            1,
        )
        self.assertEqual(
            Class.objects.all().count(),
            num_classes,
        )

    def test_create_test_enrolments(self):
        num_families = 10
        session = create_test_sessions(num_sessions=1)[0]
        enrolled_class = create_test_classes(session=session, num_classes=1)[0]

        families = []
        for i in range(num_families):
            families.append(
                create_test_family_with_students(num_children=1, num_guests=1)
            )
        create_test_enrolments(session, enrolled_class, families)

        self.assertEqual(
            Enrolment.objects.all().count(),
            num_families,
        )

        self.assertEqual(
            Enrolment.objects.filter(
                session=session,
                enrolled_class=enrolled_class,
                family__in=families,
                active=True,
            ).count(),
            num_families,
        )
