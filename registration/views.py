from rest_framework import mixins, permissions, viewsets

from .models import Family, Student
from .serializers import FamilySerializer, StudentSerializer


class FamilyViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer
    http_method_names = [
        "get",
        "post",
    ]
    permission_classes = [permissions.IsAuthenticated]
