from django.urls import NoReverseMatch, reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from enrolments.models import Enrolment, Session, Class
from registration.models import Family, Student


class EnrolmentsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@staff.com")
        parent = Student.objects.create(
            first_name="Jessica",
            last_name="Day",
            role="Parent",
        )
        self.family = Family.objects.create(
            email="fam1@test.com",
            cell_number="123456789",
            address="1 Fam St",
            preferred_comms="email",
            parent=parent,
        )
        parent.family = self.family
        parent.save()
        self.session = Session.objects.create(name="Spring 2021")
        self.class1 = Class.objects.create(
            name="Tuesday & Saturday",
            session_id=self.session.id,
            facilitator_id=self.user.id,
            attendance=[{"date": "2020-01-01", "attendees": []}],
        )
        self.class2 = Class.objects.create(
            name="Wednesday & Thursday",
            session_id=self.session.id,
            facilitator_id=self.user.id,
            attendance=[{"date": "2020-01-01", "attendees": []}],
        )
        self.enrolment = Enrolment.objects.create(
            active=True,
            family=self.family,
            session=self.session,
            preferred_class=self.class1,
            enrolled_class=self.class1,
            status=Enrolment.REGISTERED,
        )

    def test_create_enrolment(self):
        family_data = {
            "email": "brittanylau@uwblueprint.com",
            "home_number": "string",
            "cell_number": "string",
            "work_number": "string",
            "preferred_number": "Home",
            "address": "10909 Yonge St Unit 10",
            "preferred_comms": "Home",
            "parent": {
                "first_name": "Brittany",
                "last_name": "Buckets",
                "role": "Parent",
                "date_of_birth": None,
                "information": {},
            },
            "children": [
                {
                    "first_name": "Daniel",
                    "last_name": "Chen",
                    "role": "Child",
                    "date_of_birth": None,
                    "information": {},
                }
            ],
            "guests": [
                {
                    "first_name": "Lebron",
                    "last_name": "James",
                    "role": "Guest",
                    "date_of_birth": None,
                    "information": {},
                }
            ],
            "notes": "string",
        }

        url = reverse("enrolment-list")
        self.client.force_authenticate(self.user)
        request = {
            "family": family_data,
            "session": self.session.id,
            "preferred_class": self.class2.id,
            "status": Enrolment.CLASS_ALLOCATED,
        }
        response = self.client.post(url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_enrolment(self):
        url = reverse("enrolment-detail", args=[self.enrolment.id])
        self.client.force_authenticate(self.user)
        request = {
            "id": self.enrolment.id,
            "session": self.session.id,
            "preferred_class": self.class2.id,
            "enrolled_class": self.class2.id,
            "status": Enrolment.CLASS_ALLOCATED,
            "students": [self.family.parent.id],
        }
        response = self.client.put(url, request, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_not_allowed(self):
        self.client.force_authenticate(self.user)
        url = reverse("enrolment-detail", args=[self.enrolment.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized(self):
        url = reverse("enrolment-detail", args=[self.enrolment.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
