from django.core.management.base import BaseCommand
import argparse
import json
import pandas as pd
from registration.models import Family, Field, Student
from enrolments.models import Session, Enrolment, Class
from io import StringIO

PARENT_DEFAULT_FIELDS = {"first_name", "last_name"}
CHILD_DEFAULT_FIELDS = {"first_name", "last_name"}
FAMILY_DEFAULT_FIELDS = {
    "email",
    "home_number",
    "cell_number",
    "work_number",
    "address",
    "notes",
}

GUEST_RELATION_FIELD_NAME = "Relation to family"


class Command(BaseCommand):
    help = "Load a csv into database"

    def add_arguments(self, parser):
        parser.add_argument("csv", type=str)
        parser.add_argument("fields_map", type=str)
        # parser.add_argument("fields_map", type=argparse.FileType("r"))
        parser.add_argument("session_name", type=str)
        parser.add_argument("attendance_csv1", type=str)
        parser.add_argument("attendance_csv2", type=str)
        parser.add_argument("attendance_csv3", type=str)
        parser.add_argument("attendance_csv4", type=str)
        # parser.add_argument("attendance_csv5", type=str)

    def handle(self, *args, **options):
        session = Session.objects.create(name=options["session_name"])
        df = pd.read_csv(StringIO(options["csv"]), sep=",")
        records = df.to_dict(orient="records")
        print("WHY DOESWNT HTISH OFIHDLKF HSDLFKH LSKDHF", options["fields_map"])
        default_fields_map = json.loads(options["fields_map"])

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
            parent, family = self.create_parent_family(
                record, default_fields_map, options["session_name"]
            )
            self.assign_dynamic_fields(
                record, parent, parent_dynamic_fields, parent_dynamic_field_ids
            )
            self.create_children(
                record, family, default_fields_map, child_dynamic_field_ids
            )

        guest_relation_field, created = Field.objects.get_or_create(
            role=Student.GUEST,
            name=GUEST_RELATION_FIELD_NAME,
            question=GUEST_RELATION_FIELD_NAME,
            question_type=Field.TEXT,
            is_default=True,
            order=0,
        )
        session.fields = (
            list(parent_dynamic_field_ids.values())
            + list(child_dynamic_field_ids.values())
            + [guest_relation_field.id]
        )
        session.save()

        # === PARSE ATTENDANCES ===
        attendance_csvs = [
            x
            for x in [
                options["attendance_csv1"],
                options["attendance_csv2"],
                options["attendance_csv3"],
                options["attendance_csv4"],
                # options["attendance_csv5"],
            ]
            if x
        ]
        for i in range(len(attendance_csvs)):
            cls = Class.objects.create(
                name="{0} class {1}".format(options["session_name"], i + 1),
                session=session,
            )
            attendance_df = pd.read_csv(StringIO(attendance_csvs[i]), sep=",")
            attendance = attendance_df.to_dict(orient="records")
            attendance_obj = {
                date: []
                for date in attendance_df.columns.values.tolist()[3:]
                if not date.startswith("Unnamed: ") and not date == "notes"
            }
            curr_family: Family = None
            for row in attendance:
                values = list(row.values())
                first_name = "" if pd.isnull(values[1]) else values[1].strip()
                last_name = "" if pd.isnull(values[2]) else values[2].strip()
                type_indicator = values[0]
                if pd.isnull(type_indicator):
                    continue
                if not first_name or pd.isnull(first_name):
                    # No parent (nor family)
                    if type_indicator[0] == "P":
                        curr_family = None
                    continue
                student: Student = None
                # Parent
                if type_indicator[0] == "P":
                    try:
                        student = Student.objects.get(
                            first_name=first_name, last_name=last_name
                        )
                        if student.role != Student.PARENT:
                            print(
                                "Studnet {0} {1} is not a parent".format(
                                    first_name, last_name
                                )
                            )
                            continue
                        curr_family = student.family
                    except Student.DoesNotExist:
                        print(
                            "Following parent not found: {0} {1}".format(
                                first_name, last_name
                            )
                        )
                        continue
                # Caseworker
                elif type_indicator == "CW":
                    if not curr_family:
                        continue
                    student = Student.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        role=Student.GUEST,
                        family=curr_family,
                    )
                    student.information = {str(guest_relation_field.id): "Caseworker"}
                # Guest
                elif type_indicator[0] == "G":
                    if not curr_family:
                        continue
                    student = Student.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        role=Student.GUEST,
                        family=curr_family,
                    )
                # Child
                elif type_indicator[0] == "C":
                    if not curr_family:
                        continue
                    try:
                        student = Student.objects.get(
                            first_name=first_name, family=curr_family
                        )
                    except Student.DoesNotExist:
                        student = Student.objects.create(
                            first_name=first_name,
                            last_name=last_name,
                            family=curr_family,
                            role=Student.CHILD,
                        )

                enrolment, created = Enrolment.objects.get_or_create(
                    active=True,
                    session=session,
                    status=Enrolment.COMPLETED,
                    family=curr_family,
                    enrolled_class=cls,
                )
                enrolment.students.append(student.id)
                enrolment.save()

                for idx, (key, val) in enumerate(list(row.items())[3:]):
                    # Empty column
                    if key.startswith("Unnamed: ") or key == "notes":
                        continue
                    if val and not pd.isnull(val):
                        attendance_obj[key].append(student.id)
            cls_attendance = [
                {"date": date, "attendees": attendees}
                for date, attendees in attendance_obj.items()
            ]
            cls.attendance = cls_attendance
            cls.save()

    def create_dynamic_fields(self, fields, role):
        field_ids = {}
        for field in fields:
            field_obj, created = Field.objects.get_or_create(
                role=role,
                name=field,
                question=field,
                question_type=Field.TEXT,
                is_default=False,
                order=0,
            )
            field_ids[field] = field_obj.pk
        return field_ids

    def create_parent_family(self, record, fields_map, session_name):
        parent_args = {
            k: record[fields_map[k]].strip()
            for k in PARENT_DEFAULT_FIELDS
            if not pd.isnull(record[fields_map[k]])
        }
        parent_args["role"] = Student.PARENT
        parent_obj, created = Student.objects.update_or_create(
            first_name=record[fields_map["first_name"]],
            last_name=record[fields_map["last_name"]],
            defaults=parent_args,
        )

        family_args = {
            k: record[fields_map[k]].strip()
            for k in FAMILY_DEFAULT_FIELDS
            if (k in fields_map and not pd.isnull(record[fields_map[k]]))
        }
        family_obj, created = Family.objects.update_or_create(
            parent=parent_obj,
            defaults={key: family_args[key] for key in family_args if key != "notes"},
        )
        family_obj.notes = "{0}{1} {2}: {3}".format(
            family_obj.notes,
            "" if not family_obj.notes else "\n",
            session_name,
            record[fields_map["notes"]],
        )
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
            child_obj, created = Student.objects.update_or_create(
                family=family,
                first_name=record[default_fields_map["first_name"]],
                defaults=child_args,
            )
            child_obj.family = family
            child_obj.role = Student.CHILD
            dynamic_fields_dict = {
                dynamic_field_ids_map[key]: record[value]
                for key, value in dynamic_fields_map.items()
                if not pd.isnull(record[value])
            }
            child_obj.information.update(dynamic_fields_dict)
            child_obj.save()

    def assign_dynamic_fields(self, record, student, dynamic_fields, field_ids_map):
        dynamic_fields_dict = {
            field_ids_map[field_name]: record[field_name]
            for field_name in dynamic_fields
            if not pd.isnull(record[field_name])
        }
        student.information.update(dynamic_fields_dict)
        student.save()
