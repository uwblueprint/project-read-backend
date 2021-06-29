from rest_framework import mixins, permissions, viewsets
from .models import User
from .serializers import UserSerializer, UserCreateSerializer


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = [
        "get",
        "post",
    ]

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer
