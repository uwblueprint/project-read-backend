from faker import Faker

from enrolments.models import Session, Class, Enrolment
from registration.models import Field

fake = Faker()
Faker.seed(0)


def create_test_sessions(num_sessions, with_fields=False):
    sessions = []
    for i in range(num_sessions):
        sessions.append(
            Session(
                season=Session.SEASON_CHOICES[i % len(Session.SEASON_CHOICES)][1],
                year=2020 - i // len(Session.SEASON_CHOICES),
                fields=(
                    fake.random_elements(
                        elements=(
                            list(Field.objects.all().values_list("id", flat=True))
                        ),
                        length=fake.random_int(min=1, max=Field.objects.all().count()),
                        unique=True,
                    )
                )
                if with_fields
                else [],
            )
        )

    return Session.objects.bulk_create(sessions)


def create_test_classes(session, num_classes):
    classes = []
    for _ in range(num_classes):
        classes.append(
            Class(
                name=f"{fake.day_of_week()} & {fake.day_of_week()}",
                session=session,
                attendance={},
            )
        )

    return Class.objects.bulk_create(classes)


def create_test_enrolments(session, enrolled_class, families, active=True):
    enrolments = []
    for family in families:
        enrolments.append(
            Enrolment(
                family=family,
                session=session,
                enrolled_class=enrolled_class,
                active=active,
            )
        )

    Enrolment.objects.bulk_create(enrolments)
