import json
import os
from faker import Faker

from registration.models import Family, Student, Field

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


def gen_information(role):
    information = {}
    role_fields = [field for field in Field.objects.filter(role=role).values()]

    if len(role_fields) == 0:
        return information

    fields = fake.random_elements(
        elements=role_fields,
        length=fake.random_int(
            min=1,
            max=len(role_fields),
        ),
        unique=True,
    )
    for field in fields:
        field_id = str(field["id"])
        question_type = field["question_type"]
        options = field["options"]
        if question_type == Field.SELECT:
            information[field_id] = fake.random_element(elements=options)
        elif question_type == Field.MULTIPLE_SELECT:
            information[field_id] = "\n".join(
                fake.random_elements(
                    elements=options,
                    unique=True,
                )
            )
        else:
            information[field_id] = "random value"

    return information


def create_test_family(last_name, staff_user=None):
    num_interactions = fake.pyint(min_value=0, max_value=3)
    family_interactions = []
    if staff_user is not None:
        for _ in range(0, num_interactions):
            interaction = {
                "type": fake.random_element(elements=interaction_types),
                "date": fake.date(),
                "user_id": staff_user.id,
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
):
    role = Student.PARENT
    parent = Student.objects.create(
        first_name=fake.first_name(),
        role=role,
        information=gen_information(role),
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
):
    role = Student.CHILD
    children = []
    for _ in range(num_children):
        children.append(
            Student(
                first_name=fake.first_name(),
                role=role,
                date_of_birth=fake.date_this_decade().strftime("%Y-%m-%d"),
                information=gen_information(role),
                last_name=last_name,
                family=family,
            )
        )

    return Student.objects.bulk_create(children)


def create_test_guests(
    family,
    last_name,
    num_guests,
):
    role = Student.GUEST
    guests = []
    for _ in range(num_guests):
        guests.append(
            Student(
                first_name=fake.first_name(),
                role=role,
                information=gen_information(role),
                last_name=last_name,
                family=family,
            )
        )

    return Student.objects.bulk_create(guests)


def create_test_family_with_students(
    num_children,
    num_guests,
    staff_user=None,
):
    last_name = fake.unique.last_name()
    family = create_test_family(last_name=last_name, staff_user=staff_user)
    create_test_parent(
        family=family,
        last_name=last_name,
    )
    create_test_children(
        family=family,
        last_name=last_name,
        num_children=num_children,
    )
    create_test_guests(
        family=family,
        last_name=last_name,
        num_guests=num_guests,
    )
    return family
