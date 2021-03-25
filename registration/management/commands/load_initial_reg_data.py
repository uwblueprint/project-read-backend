import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction
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


def get_fields_list():
    dir = os.path.dirname(os.path.abspath(__file__))
    fields_path = os.path.join(dir, "fields.json")

    with open(fields_path, "r") as f:
        fields_data = json.loads(f.read())

    return [Field(**field) for field in fields_data]


def gen_parent_info():
    return {
        "first_name": fake.first_name(),
        "role": Student.PARENT,
        "information": {
            "1": fake.date(),
            "4": fake.random_element(elements=technologies),
            "5": "Yes" if fake.pybool() else "No",
            "6": "Yes" if fake.pybool() else "No",
            "7": fake.random_element(elements=education_levels),
        },
    }


def gen_child_info():
    return {
        "first_name": fake.first_name(),
        "role": Student.CHILD,
        "information": {
            "8": fake.random_element(elements=genders),
            "9": fake.date_this_decade().strftime("%m/%d/%Y"),
            "10": fake.random_element(elements=dietary_restrictions),
        },
    }


def gen_guest_info():
    return {
        "first_name": fake.first_name(),
        "role": Student.GUEST,
        "information": {
            "11": fake.random_element(elements=family_relations),
            "12": fake.phone_number(),
        },
    }


def create_family(has_guests=False):
    last_name = fake.unique.last_name()
    family = Family.objects.create(
        email=f"{last_name.lower()}@test.com",
        phone_number=fake.phone_number(),
        address=fake.address(),
        preferred_comms=fake.random_element(elements=preferred_comms),
    )
    parent = Student.objects.create(
        **gen_parent_info(), last_name=last_name, family=family
    )
    family.parent = parent
    family.save()

    # Create 1-3 children
    children = []
    for _ in range(fake.pyint(min_value=1, max_value=3)):
        children.append(Student(**gen_child_info(), last_name=last_name, family=family))

    # Create 0-1 guests
    guests = []
    for _ in range(1 if has_guests else fake.pyint(max_value=1)):
        guests.append(Student(**gen_guest_info(), last_name=last_name, family=family))

    Student.objects.bulk_create(children + guests)


class Command(BaseCommand):
    help = "Deletes existing field, family, and student records and creates dummy data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--num_families",
            type=int,
            help="Number of families to create",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose messages",
            default=True,
        )

    def handle(self, *args, **options):
        num_families = options.get("num_families")
        verbose = options.get("verbose")

        try:
            with transaction.atomic():
                Field.objects.all().delete()
                Family.objects.all().delete()
                Student.objects.all().delete()

                fields = get_fields_list()
                Field.objects.bulk_create(fields)

                # Create at least 1 family with guests
                create_family(has_guests=True)

                # Create n-1 families
                for _ in range(num_families - 1):
                    create_family()

            if verbose:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created {len(fields)} fields, "
                        f"{Family.objects.all().count()} families, and "
                        f"{len(Student.objects.all())} students"
                    )
                )

        except:
            if verbose:
                self.stdout.write(self.style.ERROR(f"Something went wrong"))
            raise
