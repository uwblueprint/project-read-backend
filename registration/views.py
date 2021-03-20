from rest_framework import mixins, permissions, viewsets

from .models import Family, Field
from .serializers import FamilySerializer, FamilyDetailSerializer, FieldSerializer


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

    def get_serializer_class(self):
        if self.action in ["retrieve", "create"]:
            return FamilyDetailSerializer
        return FamilySerializer

class FieldViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    http_method_names = [
        "get",
    ]
    permission_classes = [permissions.IsAuthenticated]

