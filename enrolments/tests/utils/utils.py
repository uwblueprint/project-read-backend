from faker import Faker

from enrolments.models import Session, Class, Enrolment
from registration.models import Field

fake = Faker()
Faker.seed(0)


def create_test_sessions(num_sessions, fields=[]):
    sessions = []
    for i in range(num_sessions):
        start_date = fake.date_this_decade()
        sessions.append(
            Session(
                start_date=start_date,
                name=f"{start_date.strftime('%B')} {start_date.year}",
                fields=fields,
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
                attendance=[
                    {
                        "date": str(fake.date_this_decade()),
                        "attendees": [],
                    }
                    for _ in range(32)
                ],
                colour=fake.random_element(
                    elements=[
                        "f8bbd0",
                        "e1bee7",
                        "bbdefb",
                        "b2ebf2",
                        "dcedc8",
                        "fff9c4",
                        "ffecb3",
                    ]
                ),
                days=fake.random_elements(
                    elements=[
                        Class.MONDAY,
                        Class.TUESDAY,
                        Class.WEDNESDAY,
                        Class.THURSDAY,
                        Class.FRIDAY,
                        Class.SATURDAY,
                        Class.SUNDAY,
                    ],
                    unique=True,
                ),
            )
        )

    return Class.objects.bulk_create(classes)


def create_test_enrolments(session, enrolled_class, families):
    enrolments = []
    for family in families:
        students = list(family.students.all().values_list("id", flat=True))
        enrolments.append(
            Enrolment(
                family=family,
                session=session,
                enrolled_class=enrolled_class,
                preferred_class=enrolled_class,
                status=fake.random_element(
                    elements=[status[1] for status in Enrolment.ENROLMENT_STATUSES]
                ),
                students=students,
            )
        )
        for record in enrolled_class.attendance:
            record["attendees"].extend(
                fake.random_elements(elements=students, unique=True)
            )

    enrolled_class.save()

    Enrolment.objects.bulk_create(enrolments)
