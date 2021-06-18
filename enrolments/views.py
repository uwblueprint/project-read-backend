from django.db.models import F
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Session, Class
from .serializers import (
    SessionSerializer,
    SessionDetailSerializer,
    ClassListSerializer,
    ClassDetailSerializer,
)


class SessionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Session.objects.all().order_by(F("start_date").desc(nulls_last=True))

    serializer_class = SessionSerializer
    http_method_names = [
        "get",
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SessionDetailSerializer
        return SessionSerializer

    @action(
        methods=["get"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        url_path="classes",
        url_name="classes",
    )
    def get_classes(self, request, pk=None):
        classes = Session.objects.get(id=pk).classes
        return Response(ClassListSerializer(classes, many=True).data)


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
