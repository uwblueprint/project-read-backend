from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import call, patch

from registration.models import Family, Student
from enrolments.models import Class, Session, Enrolment
from accounts.models import User
from enrolments.serializers import (
    ClassDetailSerializer,
    ClassListSerializer,
    SessionDetailSerializer,
    SessionListSerializer,
    EnrolmentSerializer,
)
from registration.serializers import FamilySerializer
from enrolments.tests.utils.utils import create_test_classes
from datetime import date

context = {"request": None}


class SessionDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            name="Spring 2020",
            fields=[1, 2, 3],
        )
        self.session_class = create_test_classes(self.session, 1)[0]
        self.other_session_class = create_test_classes(self.session, 1)[0]
        self.family = Family.objects.create(
            email="weasleys@theorder.com",
            address="12 Grimmauld Pl",
            preferred_comms="Owl Post",
        )
        self.enrolment = Enrolment.objects.create(
            active=True,
            family=self.family,
            session=self.session,
        )
        self.other_family = Family.objects.create(
            email="spongebob@squarepants.com",
            address="1 Pine Apple",
            preferred_comms="Snail Delivery",
        )
        self.other_enrolment = Enrolment.objects.create(
            active=True,
            family=self.other_family,
            session=self.session,
        )

    def test_session_detail_serializer(self):
        self.assertEqual(
            {
                "id": self.session.id,
                "name": self.session.name,
                "families": [
                    FamilySerializer(
                        self.family,
                        context={
                            "enrolment": EnrolmentSerializer(self.enrolment).data,
                        },
                    ).data,
                    FamilySerializer(
                        self.other_family,
                        context={
                            "enrolment": EnrolmentSerializer(self.other_enrolment).data
                        },
                    ).data,
                ],
                "fields": self.session.fields,
                "classes": [
                    ClassListSerializer(self.session_class).data,
                    ClassListSerializer(self.other_session_class).data,
                ],
            },
            SessionDetailSerializer(self.session, context=context).data,
        )


class ClassDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.family1 = Family.objects.create(
            email="fam1@test.com",
            cell_number="123456789",
            address="1 Fam St",
            preferred_comms="email",
        )
        self.family2 = Family.objects.create(
            email="fam2@test.com",
            cell_number="123456789",
            address="2 Fam St",
            preferred_comms="email",
        )
        self.inactive_family = Family.objects.create(
            email="fam3@test.com",
            cell_number="123406789",
            address="3 Fam St",
            preferred_comms="email",
        )
        self.session1 = Session.objects.create(name="Fall 2019")
        self.session2 = Session.objects.create(
            name="Spring 2021",
        )
        self.student1 = Student.objects.create(
            first_name="Student1 FirstName",
            last_name="Student1 LastName",
            role="Child",
            family=self.family1,
            information="null",
        )
        self.student2 = Student.objects.create(
            first_name="Student2 FirstName",
            last_name="Student2 LastName",
            role="Child",
            family=self.family2,
            information="null",
        )
        self.facilitator = User.objects.create(email="user@staff.com")
        self.class1 = Class.objects.create(
            name="Test Class 1",
            session_id=self.session1.id,
            facilitator_id=self.facilitator.id,
            attendance=[{"date": "2020-01-01", "attendees": [1, 2]}],
        )
        self.empty_class = Class.objects.create(
            name="Test Empty Class",
            session_id=self.session2.id,
            facilitator_id=self.facilitator.id,
            attendance=[{"date": "2020-01-01", "attendees": []}],
        )
        self.enrolment1 = Enrolment.objects.create(
            active=True,
            family=self.family1,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )
        self.enrolment2 = Enrolment.objects.create(
            active=True,
            family=self.family2,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )
        self.inactive_enrolment = Enrolment.objects.create(
            active=False,
            family=self.inactive_family,
            session=self.session1,
            preferred_class=self.class1,
            enrolled_class=self.class1,
        )

    def test_class_detail_serializer(self):
        self.assertEqual(
            {
                "id": self.class1.id,
                "name": self.class1.name,
                "attendance": self.class1.attendance,
                "families": [
                    FamilySerializer(
                        self.family1,
                        context={
                            "request": None,
                            "enrolment": EnrolmentSerializer(self.enrolment1).data,
                        },
                    ).data,
                    FamilySerializer(
                        self.family2,
                        context={
                            "request": None,
                            "enrolment": EnrolmentSerializer(self.enrolment2).data,
                        },
                    ).data,
                ],
            },
            ClassDetailSerializer(self.class1, context={"request": None}).data,
        )

    def test_class_detail_serializer__empty_class(self):
        self.assertEqual(
            {
                "id": self.empty_class.id,
                "name": self.empty_class.name,
                "attendance": self.empty_class.attendance,
                "families": [],
            },
            ClassDetailSerializer(self.empty_class, context={"request": None}).data,
        )


class EnrolmentSerializerTestCase(TestCase):
    def setUp(self):
        parent = Student.objects.create(
            first_name="Gollum", last_name="Goat", role=Student.PARENT
        )
        self.family = Family.objects.create(
            parent=parent,
            email="justkeepswimming@ocean.com",
            cell_number="123456789",
            address="1 Test Ave",
            preferred_comms="Dolphin Whistle",
        )
        parent.family = self.family
        parent.save()
        self.session = Session.objects.create(
            name="Spring 201",
            start_date=date(2021, 5, 15),
        )
        self.other_session = Session.objects.create(
            name="Fall 2021",
            start_date=date(2021, 9, 15),
        )
        self.class1 = Class.objects.create(
            name="Tuesday & Saturday",
            session_id=self.session.id,
            facilitator_id=None,
            attendance=[],
        )
        self.class2 = Class.objects.create(
            name="Wednesday & Thursday",
            session_id=self.session.id,
            facilitator_id=None,
            attendance=[],
        )
        self.class_not_in_session = Class.objects.create(
            name="Wednesday & Thursday",
            session_id=self.other_session.id,
            facilitator_id=None,
            attendance=[],
        )
        self.enrolment = Enrolment.objects.create(
            active=False,
            family=self.family,
            session=self.session,
            preferred_class=self.class1,
            enrolled_class=self.class2,
            status=Enrolment.REGISTERED,
        )
        self.update_request = {
            "id": self.enrolment.id,
            "session": self.session.id,
            "preferred_class": self.class2.id,
            "enrolled_class": self.class1.id,
            "status": Enrolment.CLASS_ALLOCATED,
            "students": [self.family.parent.id],
        }

    def test_enrolment_serializer(self):
        self.assertEqual(
            {
                "id": self.enrolment.id,
                "session": SessionListSerializer(self.session).data,
                "preferred_class": ClassListSerializer(self.class1).data,
                "enrolled_class": ClassListSerializer(self.class2).data,
                "status": self.enrolment.status,
                "students": [],
            },
            EnrolmentSerializer(self.enrolment).data,
        )

    def test_enrolment_serializer__no_classes(self):
        self.enrolment.preferred_class = None
        self.enrolment.enrolled_class = None
        self.assertEqual(
            {
                "id": self.enrolment.id,
                "session": SessionListSerializer(self.session).data,
                "preferred_class": None,
                "enrolled_class": None,
                "status": self.enrolment.status,
                "students": [],
            },
            EnrolmentSerializer(self.enrolment).data,
        )

    def test_enrolment_update(self):
        serializer = EnrolmentSerializer(self.enrolment, data=self.update_request)
        self.assertTrue(serializer.is_valid())

    def test_enrolment_update__read_only_session(self):
        data = dict(self.update_request)
        data["session"] = self.other_session.id
        serializer = EnrolmentSerializer(self.enrolment, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(self.enrolment.session, self.session)

    @patch("enrolments.serializers.validate_student_ids_in_family")
    @patch("enrolments.serializers.validate_class_in_session")
    def test_enrolment_update_validate(
        self,
        mock_validate_class_in_session,
        validate_student_ids_in_family,
    ):
        serializer = EnrolmentSerializer(self.enrolment, data=self.update_request)
        self.assertTrue(serializer.is_valid())
        validate_student_ids_in_family.assert_called_once_with(
            [self.family.parent.id],
            self.family,
        )
        self.assertEqual(mock_validate_class_in_session.call_count, 2)
        mock_validate_class_in_session.assert_has_calls(
            [
                call(self.class2, self.session),
                call(self.class1, self.session),
            ]
        )

    @patch(
        "enrolments.serializers.validate_student_ids_in_family",
        side_effect=ValidationError(""),
    )
    @patch("enrolments.serializers.validate_class_in_session")
    def test_enrolment_update_validate__invalid_students(
        self,
        mock_validate_class_in_session,
        validate_student_ids_in_family,
    ):
        serializer = EnrolmentSerializer(self.enrolment, data=self.update_request)
        self.assertFalse(serializer.is_valid())
        validate_student_ids_in_family.assert_called_once_with(
            [self.family.parent.id],
            self.family,
        )
        mock_validate_class_in_session.assert_not_called()

    @patch(
        "enrolments.serializers.validate_student_ids_in_family",
    )
    @patch(
        "enrolments.serializers.validate_class_in_session",
        side_effect=ValidationError(""),
    )
    def test_enrolment_update_validate__invalid_classes(
        self,
        mock_validate_class_in_session,
        validate_student_ids_in_family,
    ):
        serializer = EnrolmentSerializer(self.enrolment, data=self.update_request)
        self.assertFalse(serializer.is_valid())
        validate_student_ids_in_family.assert_called_once_with(
            [self.family.parent.id],
            self.family,
        )
        mock_validate_class_in_session.assert_called_once_with(
            self.class2,
            self.session,
        )
