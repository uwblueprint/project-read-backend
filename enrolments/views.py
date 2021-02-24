from rest_framework import mixins, permissions, viewsets

from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    http_method_names = [
        "get",
    ]

    permission_classes = [permissions.IsAuthenticated]
