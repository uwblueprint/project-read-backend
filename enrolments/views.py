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
    ClassDetailSerializer,
    EnrolmentCreateSerializer,
    EnrolmentSerializer,
)


class SessionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Session.objects.all().order_by(F("start_date").desc(nulls_last=True))
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
):
    queryset = Class.objects.all()
    serializer_class = ClassDetailSerializer
    http_method_names = [
        "get",
        "put",
    ]
    permission_classes = [permissions.IsAuthenticated]


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
        if self.action == "create":
            return EnrolmentCreateSerializer
        return EnrolmentSerializer


class ExportClassesView(APIView):
    queryset = Class.objects.all()
    renderer_classes = [r.CSVRenderer]

    def get(self, request, format=None):
        return Response(list(Class.objects.values()))


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
