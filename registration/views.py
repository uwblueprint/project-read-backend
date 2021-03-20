from rest_framework import mixins, permissions, viewsets

from .models import Family
from .serializers import FamilySerializer, FamilyDetailSerializer


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
