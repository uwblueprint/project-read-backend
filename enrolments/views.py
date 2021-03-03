from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Session
from .serializers import (
    SessionSerializer,
    SessionDetailsSerializer,
    ClassListSerializer,
)


class SessionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    http_method_names = [
        "get",
    ]
    permission_classes = [permissions.IsAuthenticated]

    @action(
        methods=["get"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        url_path="classes",
        url_name="classes",
    )
    def get_classes(self, request, pk=None):
        classes = Session.objects.filter(id=pk).first().classes
        return Response(ClassListSerializer(classes, many=True).data)
