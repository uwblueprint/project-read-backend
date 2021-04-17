from faker import Faker

from enrolments.models import Session, Class, Enrolment

fake = Faker()
Faker.seed(0)


def create_test_sessions(num_sessions):
    sessions = []
    for i in range(num_sessions):
        sessions.append(
            Session(
                season=Session.SEASON_CHOICES[i % len(Session.SEASON_CHOICES)][1],
                year=2020 - i // len(Session.SEASON_CHOICES),
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
