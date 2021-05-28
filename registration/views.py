from rest_framework import mixins, permissions, viewsets, status

from .models import Family, Field
from .serializers import FamilySerializer, FamilyDetailSerializer, FieldSerializer, FamilySearchSerializer
from rest_framework.response import Response 
from rest_framework.decorators import action


class FamilyViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Family.objects.all()
    http_method_names = [
        "get",
        "post",
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["retrieve", "create"]:
            return FamilyDetailSerializer
        return FamilySerializer

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path="search",
        url_name="search",
    )
    def search(self, request):
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        if not first_name and not last_name: 
            return Response("No search parameters found.", status=status.HTTP_400_BAD_REQUEST)
        result = Family.objects
        if first_name: 
            result = result.filter(parent__first_name__iexact=first_name)
        if last_name: 
            result = result.filter(parent__last_name__iexact=last_name)

        # how granular / accepting is our search, do we want to be able to search by parts of first names / last names ?
        return Response(FamilySearchSerializer(result, many=True, context={"request" : None}).data)


class FieldViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    http_method_names = [
        "get",
    ]
    permission_classes = [permissions.IsAuthenticated]
