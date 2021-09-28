from django.db.models import F
from rest_framework import mixins, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_csv import renderers as r

from .models import Class, Enrolment, Session
from .serializers import (
    SessionListSerializer,
    SessionDetailSerializer,
    SessionCreateSerializer,
    ClassDetailSerializer,
    ClassCreateSerializer,
    EnrolmentSerializer,
)


class SessionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Session.objects.all().order_by(F("start_date").asc(nulls_last=True))
    http_method_names = [
        "get",
        "post",
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SessionDetailSerializer
        elif self.action == "create":
            return SessionCreateSerializer
        return SessionListSerializer


class ClassViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Class.objects.all()
    serializer_class = ClassDetailSerializer
    http_method_names = [
        "get",
        "post",
        "put",
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return ClassCreateSerializer
        return ClassDetailSerializer


class EnrolmentViewSet(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin
):
    queryset = Enrolment.objects.all()
    http_method_names = [
        "post",
        "put",
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return EnrolmentSerializer


class ExportClassesView(APIView):
    queryset = Class.objects.all()
    renderer_classes = [r.CSVRenderer]

    def get(self, request, format=None):
        # return all fields except attendance
        return Response(list(Class.objects.values(*[field.name for field in Class._meta.fields if field.name != "attendance"])))

class ExportAttendancesView(APIView):
    queryset = Class.objects.all()
    renderer_classes = [r.CSVRenderer]

    def get(self, request, format=None):
        class_id = request.query_params.get("class_id")
        attendance = Class.objects.get(pk=class_id).attendance
        print(attendance, len(attendance))
        # Transform to {date: set_of_attendees, ...}
        attendance = {obj["date"]: set(obj["attendees"]) for obj in attendance}
        # flatten attendance.values() to get set of attendees
        attendees = set(attendee for attendees in list(attendance.values()) for attendee in attendees)
        res = []
        for attendee in attendees:
            attendee_attendance = {"student_id": attendee}
            for date in attendance.keys():
                attendee_attendance[date] = 1 if attendee in attendance[date] else 0
            res.append(attendee_attendance)
        return Response(res)
        # for date in attendance.keys():
        #     csv += date + ","
        # csv += "\n"
        # # flatten attendance.values()
        # attendees = set(attendee for attendees in list(attendance.values()) for attendee in attendees)
        # for attendee in attendees:
        #     row = str(attendee) + ","
        #     for date in attendance.keys():
        #         if attendee in attendance[date]:
        #             row += "1,"
        #         else:
        #             row += "0,"
        #     csv += row + "\n"


class ExportEnrolmentsView(APIView):
    queryset = Enrolment.objects.all()
    renderer_classes = [r.CSVRenderer]

    def get(self, request, format=None):
        return Response(list(Enrolment.objects.values()))


class ExportSessionsView(APIView):
    queryset = Session.objects.all()
    renderer_classes = [r.CSVRenderer]

    def get(self, request, format=None):
        return Response(list(Session.objects.values()))
