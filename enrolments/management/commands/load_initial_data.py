from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from accounts.models import User
from enrolments.models import Session, Class, Enrolment
from registration.models import Family, Student, Field
import enrolments.tests.utils.utils as enrolment_utils
import registration.tests.utils.utils as registration_utils
import accounts.tests.utils.utils as account_utils

fake = Faker()


class Command(BaseCommand):
    help = "Deletes existing field, family, and student records and creates dummy data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--families",
            type=int,
            nargs="?",
            default=100,
            help="Number of families to create",
        )
        parser.add_argument(
            "--sessions",
            type=int,
            nargs="?",
            default=5,
            help="Number of sessions to create",
        )
        parser.add_argument(
            "--classes_per_session",
            type=int,
            nargs="?",
            default=3,
            help="Number of classes per session",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose messages",
            default=True,
        )

    def handle(self, *args, **options):
        num_families = options.get("families")
        num_sessions = options.get("sessions")
        num_classes_per_session = options.get("classes_per_session")
        verbose = options.get("verbose")

        try:
            with transaction.atomic():
                Enrolment.objects.all().delete()
                Class.objects.all().delete()
                Session.objects.all().delete()
                Field.objects.all().delete()
                Family.objects.all().delete()
                Student.objects.all().delete()
                User.objects.filter(email="user@test.com").delete()

                registration_utils.create_test_fields()
                staff_user = account_utils.create_staff_user()
                for _ in range(num_families):
                    registration_utils.create_test_family_with_students(
                        num_children=fake.pyint(min_value=1, max_value=3),
                        num_guests=fake.pyint(max_value=1),
                        staff_user=staff_user,
                    )

                sessions = enrolment_utils.create_test_sessions(
                    num_sessions,
                    fields=fake.random_elements(
                        elements=(
                            list(Field.objects.all().values_list("id", flat=True))
                        ),
                        length=fake.random_int(min=1, max=Field.objects.all().count()),
                        unique=True,
                    ),
                )

                classes = []
                for session in sessions:
                    classes.extend(
                        enrolment_utils.create_test_classes(
                            session=session,
                            num_classes=num_classes_per_session,
                        )
                    )

                num_classes = num_sessions * num_classes_per_session
                num_families_per_class = -(
                    -num_families // num_classes
                )  # ceiling division (upside-down floor division)
                for i, class_ in enumerate(classes):
                    enrolment_utils.create_test_enrolments(
                        session=class_.session,
                        enrolled_class=class_,
                        families=Family.objects.all()[
                            (i * num_families_per_class) : (i + 1)
                            * num_families_per_class
                        ],
                    )

            if verbose:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created {Field.objects.all().count()} fields, "
                        f"{Family.objects.all().count()} families, and "
                        f"{len(Student.objects.all())} students"
                    )
                )

        except:
            if verbose:
                self.stdout.write(self.style.ERROR(f"Something went wrong"))
            raise
