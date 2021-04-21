from django.test import TestCase
from registration.models import Student, Family, Field
from accounts.models import User
from enrolments.models import Enrolment, Class, Session
from enrolments.validators import (
    validate_attendance,
    validate_schema,
    validate_class_in_session,
    validate_enrolment,
    validate_fields,
    validate_students_in_enrolment,
)
from django.core.exceptions import ValidationError
from unittest.mock import patch


class EnrolmentValidatorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@staff.com")
        self.family = Family.objects.create(
            email="fam1@test.com",
            cell_number="123456789",
            address="1 Fam Ave",
            preferred_comms="email",
        )
        self.session = Session.objects.create(season=Session.FALL, year="2020")
        self.class_in_session = Class.objects.create(
            name="Class in session",
            session=self.session,
            facilitator=self.user,
            attendance={},
        )

    def test_validate_classes_in_session(self):
        class_no_sessions = Class.objects.create(
            name="Class with no sessions",
            session=None,
            facilitator=self.user,
            attendance={},
        )
        session_other = Session.objects.create(season=Session.SPRING, year="2020")
        self.assertIsNone(
            validate_class_in_session(self.class_in_session, self.session)
        )
        self.assertRaises(
            ValidationError, validate_class_in_session, class_no_sessions, self.session
        )
        self.assertRaises(
            ValidationError,
            validate_class_in_session,
            self.class_in_session,
            session_other,
        )

    @patch("enrolments.validators.validate_class_in_session")
    def test_validate_enrolments(self, mock_validate):
        enrolment = Enrolment(
            family=self.family,
            session=self.session,
            preferred_class=self.class_in_session,
            enrolled_class=self.class_in_session,
        )
        self.assertIsNone(validate_enrolment(enrolment))
        mock_validate.assert_called_with(self.class_in_session, self.session)

    @patch(
        "enrolments.validators.validate_class_in_session",
        side_effect=ValidationError(""),
    )
    def test_validate_enrolments__invalid(self, mock_validate):
        enrolment = Enrolment(
            family=self.family,
            session=self.session,
            preferred_class=self.class_in_session,
            enrolled_class=self.class_in_session,
        )
        self.assertRaises(ValidationError, validate_enrolment, enrolment)
        mock_validate.assert_called_once_with(self.class_in_session, self.session)

    def test_validate_students_in_enrolment(self):
        parent = Student.objects.create(
            first_name="Daddy",
            last_name="McDonald",
            role=Student.PARENT,
            family=self.family,
        )
        child = Student.objects.create(
            first_name="Lil Tom",
            last_name="McDonald",
            role=Student.CHILD,
            family=self.family,
        )
        other_family = Family.objects.create(
            email="fam2@test.com",
            phone_number="923456789",
            address="2 Fam Ave",
            preferred_comms="email",
        )
        other_child = Student.objects.create(
            first_name="Yohan",
            last_name="Wilkshire",
            role=Student.CHILD,
            family=other_family,
        )
        enrolment = Enrolment.objects.create(
            active=True,
            family=self.family,
            session=self.session,
            preferred_class=self.class_in_session,
            enrolled_class=self.class_in_session,
            students=[child.id],
        )
        enrolment_extra_student = Enrolment.objects.create(
            active=True,
            family=self.family,
            session=self.session,
            preferred_class=self.class_in_session,
            enrolled_class=self.class_in_session,
            students=[child.id, other_child.id],
        )

        self.assertIsNone(validate_students_in_enrolment(enrolment))
        self.assertRaises(
            ValidationError, validate_students_in_enrolment, enrolment_extra_student
        )


class AttendanceValidatorTestCase(TestCase):
    def setUp(self):
        Student.objects.bulk_create(
            [
                Student(first_name="Brittany", last_name="Buckets", role="Parent"),
                Student(first_name="Buckets", last_name="Jr", role="Child"),
            ]
        )
        Field.objects.bulk_create(
            [
                Field(
                    role=Field.PARENT,
                    name="Drip or drown?",
                    question="Do you have drip?",
                    question_type=Field.TEXT,
                    is_default=False,
                    order=1,
                ),
                Field(
                    role=Field.CHILD,
                    name="Swag or square?",
                    question="Do you have swag?",
                    question_type=Field.TEXT,
                    is_default=True,
                    order=2,
                ),
                Field(
                    role=Field.GUEST,
                    name="Ice or ill?",
                    question="Do you have ice?",
                    question_type=Field.TEXT,
                    is_default=False,
                    order=3,
                ),
            ]
        )
        self.field_ids = list(Field.objects.values_list("id", flat=True))
        self.student_ids = list(Student.objects.values_list("id", flat=True))
        self.session = Session.objects.create(
            season=Session.SPRING, year=2021, fields=self.field_ids
        )

    def test_attendance_date_format(self):
        obj1 = [{"date": "2021-04-19", "attendees": []}]
        obj2 = [{"date": "2021/04/19", "attendees": []}]
        obj3 = [{"date": "2021-99-99", "attendees": []}]
        self.assertEqual(validate_attendance(obj1), None)
        self.assertRaises(ValidationError, validate_attendance, obj2)
        self.assertRaises(ValidationError, validate_attendance, obj3)

    def test_attendees_exist(self):
        obj1 = [{"date": "2021-04-19", "attendees": self.student_ids}]
        obj2 = [{"date": "2021-04-19", "attendees": [999]}]
        obj3 = [{"date": "2021-04-19", "attendees": self.student_ids + [999]}]
        self.assertEqual(validate_attendance(obj1), None)
        self.assertRaises(ValidationError, validate_attendance, obj2)
        self.assertRaises(ValidationError, validate_attendance, obj3)

    def test_fields_exist(self):
        obj1 = self.session.fields
        obj2 = [self.field_ids] + [999]
        obj3 = None
        self.assertEqual(validate_fields(obj1), None)
        self.assertRaises(ValidationError, validate_fields, obj2)
        self.assertRaises(ValidationError, validate_fields, obj3)


class SchemaValidatorTestCase(TestCase):
    def test_simple_valid(self):
        json = [
            {"date": "2021-04-19", "attendees": [1, 2, 3]},
            {"date": "2021-04-11", "attendees": [1, 2, 3]},
        ]
        schema = [{"date": "str", "attendees": ["int"]}]
        self.assertTrue(validate_schema(json, schema))

    def test_missing_list(self):
        json = [
            {"date": "2021-04-19", "attendees": [1, 2, 3]},
            {"date": "2021-04-11", "attendees": [1, 2, 3]},
        ]
        schema = [{"date": "str", "attendees": "int"}]
        self.assertFalse(validate_schema(json, schema))

    def test_wrong_type(self):
        json = [
            {"date": "2021-04-19", "attendees": [1, 2, 3]},
            {"date": "2021-04-11", "attendees": [1, 2, 3]},
        ]
        schema = [{"date": "str", "attendees": ["str"]}]
        self.assertFalse(validate_schema(json, schema))

    def test_missing_field(self):
        json = [
            {"date": "2021-04-19", "attendees": [1, 2, 3]},
            {
                "date": "2021-04-11",
            },
        ]
        schema = [{"date": "str", "attendees": ["int"]}]
        self.assertFalse(validate_schema(json, schema))

    def test_extra_field_no_strict(self):
        json = [
            {"date": "2021-04-19", "attendees": [1, 2, 3]},
            {"date": "2021-04-11", "attendees": [1, 2, 3], "extra": 20},
        ]
        schema = [{"date": "str", "attendees": ["int"]}]
        self.assertTrue(validate_schema(json, schema))

    def test_extra_field_strict(self):
        json = [
            {"date": "2021-04-19", "attendees": [1, 2, 3]},
            {"date": "2021-04-11", "attendees": [1, 2, 3], "extra": 20},
        ]
        schema = [{"date": "str", "attendees": ["int"]}]
        self.assertFalse(validate_schema(json, schema, True))

    def test_nested(self):
        json = [
            {
                "field1": [
                    {
                        "field2": 30,
                        "field3": ["str1", "str2", "str3"],
                        "field4": [
                            {"field5": {"field6": [3.2, 3.1, 3.7], "field7": True}}
                        ],
                    }
                ],
                "field2": ["a", "b", "c"],
                "field3": -6,
            },
            {
                "field1": [
                    {
                        "field2": 2,
                        "field3": ["asd", "qwe"],
                        "field4": [
                            {"field5": {"field6": [1.0, 2.3, 1.2], "field7": False}},
                            {"field5": {"field6": [3.0, 4.0, 1.2], "field7": True}},
                        ],
                    }
                ],
                "field2": [],
                "field3": 111,
            },
        ]
        schema = [
            {
                "field1": [
                    {
                        "field2": "int",
                        "field3": ["str"],
                        "field4": [{"field5": {"field6": ["float"], "field7": "bool"}}],
                    }
                ],
                "field2": ["str"],
                "field3": "int",
            }
        ]
        self.assertTrue(validate_schema(json, schema))
