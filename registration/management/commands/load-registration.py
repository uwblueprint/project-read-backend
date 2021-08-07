from django.core.management.base import BaseCommand
import argparse
import json
import pandas as pd
from registration.models import Family, Field, Student

PARENT_DEFAULT_FIELDS = {"first_name", "last_name"}
CHILD_DEFAULT_FIELDS = {"first_name", "last_name"}
FAMILY_DEFAULT_FIELDS = {
    "email",
    "home_number",
    "cell_number",
    "work_number",
    "address",
}


class Command(BaseCommand):
    help = "Load a csv into database"

    def add_arguments(self, parser):
        parser.add_argument("csv", type=argparse.FileType("r"))
        parser.add_argument("fields_map", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        df = pd.read_csv(options["csv"])
        records = df.to_dict(orient="records")
        default_fields_map = json.load(options["fields_map"])

        parent_default_fields = set()
        parent_dynamic_fields = set()
        child_default_fields = set()
        child_dynamic_fields = set()
        child_dynamic_fields_internal = set()

        if "children" not in default_fields_map:
            raise KeyError
        for child in default_fields_map["children"]:
            child_default_fields.update(set(child["default_fields"].values()))
            child_dynamic_fields.update(set(child["dynamic_fields"].values()))
            child_dynamic_fields_internal.update(set(child["dynamic_fields"].keys()))

        parent_default_fields.update(
            set([value for value in default_fields_map.values() if type(value) == str])
        )
        parent_dynamic_fields.update(
            set(df.columns)
            - parent_default_fields
            - child_default_fields
            - child_dynamic_fields
        )
        parent_dynamic_field_ids = self.create_dynamic_fields(
            parent_dynamic_fields, Student.PARENT
        )
        child_dynamic_field_ids = self.create_dynamic_fields(
            child_dynamic_fields_internal, Student.CHILD
        )

        for record in records:
            parent, family = self.create_parent_family(record, default_fields_map)
            self.assign_dynamic_fields(
                record, parent, parent_dynamic_fields, parent_dynamic_field_ids
            )
            self.create_children(
                record, family, default_fields_map, child_dynamic_field_ids
            )

    def create_dynamic_fields(self, fields, role):
        field_ids = {}
        for field in fields:
            field_obj = Field.objects.create(
                role=role,
                name=field,
                question=field,
                question_type=Field.TEXT,
                is_default=False,
                order=0,
            )
            field_ids[field] = field_obj.pk
        return field_ids

    def create_parent_family(self, record, fields_map):
        parent_args = {
            k: record[fields_map[k]]
            for k in PARENT_DEFAULT_FIELDS
            if not pd.isnull(record[fields_map[k]])
        }
        parent_args["role"] = Student.PARENT
        parent_obj = Student.objects.create(**parent_args)
        parent_obj.save()

        family_args = {
            k: record[fields_map[k]]
            for k in FAMILY_DEFAULT_FIELDS
            if not pd.isnull(record[fields_map[k]])
        }
        family_obj = Family.objects.create(**family_args)
        family_obj.parent = parent_obj
        family_obj.save()

        parent_obj.family = family_obj
        parent_obj.save()

        return parent_obj, family_obj

    def create_children(self, record, family, fields_map, dynamic_field_ids_map):
        for idx in range(len(fields_map["children"])):
            default_fields_map = fields_map["children"][idx]["default_fields"]
            dynamic_fields_map = fields_map["children"][idx]["dynamic_fields"]
            child_args = {
                k: record[default_fields_map[k]]
                for k in CHILD_DEFAULT_FIELDS
                if not pd.isnull(record[fields_map[k]])
            }
            if all([pd.isnull(val) for val in child_args.values()]):
                continue
            child_obj = Student.objects.create(**child_args)
            child_obj.family = family
            child_obj.role = Student.CHILD
            dynamic_fields_dict = {
                dynamic_field_ids_map[key]: record[value]
                for key, value in dynamic_fields_map.items()
                if not pd.isnull(record[value])
            }
            child_obj.information = dynamic_fields_dict
            child_obj.save()

    def assign_dynamic_fields(self, record, student, dynamic_fields, field_ids_map):
        dynamic_fields_dict = {
            field_ids_map[field_name]: record[field_name]
            for field_name in dynamic_fields
            if not pd.isnull(record[field_name])
        }
        student.information = dynamic_fields_dict
        student.save()
