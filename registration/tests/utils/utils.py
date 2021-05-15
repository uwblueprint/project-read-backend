import json
import os
from faker import Faker

from registration.models import Family, Student, Field

fake = Faker()

# Sample options
preferred_comms = {"Phone", "Email"}
technologies = {"Laptop", "Tablet", "Desktop"}
education_levels = {"High School", "Trade School", "College/University", "Masters"}
genders = {"Man", "Woman", "Non-binary", "Other"}
dietary_restrictions = {"Peanuts", "Dairy", "Eggs", "Nuts", "Vegetarian", "Vegan"}
family_relations = {
    "Grandmother",
    "Grandfather",
    "Mother",
    "Father",
    "Aunt",
    "Uncle",
    "Sibling",
    "Friend",
}


def create_test_fields():
    dir = os.path.dirname(os.path.abspath(__file__))
    fields_path = os.path.join(dir, "fields.json")

    with open(fields_path, "r") as f:
        fields_data = json.loads(f.read())

    return Field.objects.bulk_create([Field(**field) for field in fields_data])


def create_test_family(last_name):
    return Family.objects.create(
        email=f"{last_name.lower()}@test.com",
        cell_number=fake.phone_number(),
        work_number=fake.phone_number(),
        home_number=fake.phone_number(),
        preferred_number=fake.random_element(elements=Family.NUMBER_PREF_CHOICES)[1],
        address=fake.address(),
        preferred_comms=fake.random_element(elements=preferred_comms),
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
            "4": fake.random_element(elements=technologies),
            "5": "Yes" if fake.pybool() else "No",
            "6": "Yes" if fake.pybool() else "No",
            "7": fake.random_element(elements=education_levels),
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
                information={
                    "8": fake.random_element(elements=genders),
                    "9": fake.date_this_decade().strftime("%m/%d/%Y"),
                    "10": fake.random_element(elements=dietary_restrictions),
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
                    "11": fake.random_element(elements=family_relations),
                    "12": fake.phone_number(),
                }
                if with_fields
                else {},
                last_name=last_name,
                family=family,
            )
        )

    return Student.objects.bulk_create(guests)


def create_test_family_with_students(
    num_children,
    num_guests,
    with_fields=False,
):
    last_name = fake.unique.last_name()
    family = create_test_family(last_name=last_name)
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
