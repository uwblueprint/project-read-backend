from django.db.models import F
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.management import call_command

from .models import Class, Enrolment, Session
from .serializers import (
    SessionListSerializer,
    SessionDetailSerializer,
    ClassDetailSerializer,
    ClassCreateSerializer,
    EnrolmentSerializer,
)


class SessionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Session.objects.all().order_by(F("start_date").asc(nulls_last=True))
    http_method_names = [
        "get",
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SessionDetailSerializer
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


class ImportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        students_csv = request.POST['students_csv']
        fields_map = request.POST["fields_map"]
        session_name = request.POST["session_name"]
        attendance_csv1 = request.POST["attendance_csv1"]
        attendance_csv2 = request.POST["attendance_csv2"]
        attendance_csv3 = request.POST["attendance_csv3"]
        # attendance_csv4 = self.request.FILES.get("attendance_csv4")
        call_command(
            "load-registration",
            students_csv,
            fields_map,
            session_name,
            attendance_csv1,
            attendance_csv2,
                        attendance_csv3,
        )
        return Response("data imported", status=status.HTTP_201_CREATED)
