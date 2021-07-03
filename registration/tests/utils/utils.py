import json
import os
from faker import Faker

from registration.models import Family, Student, Field
from accounts.models import User

fake = Faker()

# Sample options
preferred_comms = {"Phone", "Email"}
interaction_types = {"Phone call", "Email"}


def create_test_fields():
    dir = os.path.dirname(os.path.abspath(__file__))
    fields_path = os.path.join(dir, "fields.json")

    with open(fields_path, "r") as f:
        fields_data = json.loads(f.read())

    return Field.objects.bulk_create([Field(**field) for field in fields_data])


def create_test_family(last_name, staff_user=None):
    num_interactions = fake.pyint(min_value=0, max_value=3)
    family_interactions = []
    if staff_user is not None:
        for _ in range(0, num_interactions):
            interaction = {
                "type": fake.random_element(elements=interaction_types),
                "date": fake.date(),
                "user_id": staff_user.id,
                "user_email": staff_user.email,
            }
            family_interactions.append(interaction)

    return Family.objects.create(
        email=f"{last_name.lower()}@test.com",
        cell_number=fake.phone_number(),
        work_number=fake.phone_number(),
        home_number=fake.phone_number(),
        preferred_number=fake.random_element(elements=Family.NUMBER_PREF_CHOICES)[1],
        address=fake.address(),
        preferred_comms=fake.random_element(elements=preferred_comms),
        notes=fake.text(max_nb_chars=60),
        interactions=family_interactions,
    )


def create_test_parent(
    family,
    last_name,
    with_fields=False,
):
    parent = Student.objects.create(
        first_name=fake.first_name(),
        role=Student.PARENT,
        information={
            "1": fake.date(),
            "4": fake.random_element(elements=Field.objects.get(id=4).options),
            "5": fake.random_element(elements=Field.objects.get(id=5).options),
            "6": fake.random_element(elements=Field.objects.get(id=6).options),
            "7": fake.random_element(elements=Field.objects.get(id=7).options),
        }
        if with_fields
        else {},
        last_name=last_name,
        family=family,
    )

    family.parent = parent
    family.save()

    return parent


def create_test_children(
    family,
    last_name,
    num_children,
    with_fields=False,
):
    children = []
    for _ in range(num_children):
        children.append(
            Student(
                first_name=fake.first_name(),
                role=Student.CHILD,
                date_of_birth=fake.date_this_decade().strftime("%Y-%m-%d"),
                information={
                    "8": fake.random_element(elements=Field.objects.get(id=8).options),
                    "9": fake.random_element(elements=Field.objects.get(id=9).options),
                }
                if with_fields
                else {},
                last_name=last_name,
                family=family,
            )
        )

    return Student.objects.bulk_create(children)


def create_test_guests(
    family,
    last_name,
    num_guests,
    with_fields=False,
):
    guests = []
    for _ in range(num_guests):
        guests.append(
            Student(
                first_name=fake.first_name(),
                role=Student.GUEST,
                information={
                    "10": fake.random_element(
                        elements=Field.objects.get(id=10).options
                    ),
                    "11": fake.phone_number(),
                }
                if with_fields
                else {},
                last_name=last_name,
                family=family,
            )
        )

    return Student.objects.bulk_create(guests)


def create_test_family_with_students(
    num_children, num_guests, with_fields=False, staff_user=None
):
    last_name = fake.unique.last_name()
    family = create_test_family(last_name=last_name, staff_user=staff_user)
    create_test_parent(
        family=family,
        last_name=last_name,
        with_fields=with_fields,
    )
    create_test_children(
        family=family,
        last_name=last_name,
        with_fields=with_fields,
        num_children=num_children,
    )
    create_test_guests(
        family=family,
        last_name=last_name,
        with_fields=with_fields,
        num_guests=num_guests,
    )
    return family
