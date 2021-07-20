from django.db.models import F
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Enrolment, Session, Class
from .serializers import (
    SessionListSerializer,
    SessionDetailSerializer,
    ClassDetailSerializer,
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
):
    queryset = Class.objects.all()
    serializer_class = ClassDetailSerializer
    http_method_names = [
        "get",
    ]
    permission_classes = [permissions.IsAuthenticated]


class EnrolmentViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    queryset = Enrolment.objects.all()
    serializer_class = EnrolmentSerializer
    http_method_names = [
        "put",
    ]
    permission_classes = [permissions.IsAuthenticated]
