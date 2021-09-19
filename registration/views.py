from rest_framework import mixins, permissions, viewsets, status
from rest_framework.views import APIView

from .models import Family, Field, Student
from .serializers import (
    FamilySerializer,
    FamilyDetailSerializer,
    FieldSerializer,
    FamilySearchSerializer,
    StudentListSerializer,
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_csv import renderers as r


class FamilyViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = Family.objects.all()
    http_method_names = [
        "get",
        "post",
        "put",
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["retrieve", "create", "update"]:
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
        parent_only = self.request.query_params.get("parent_only")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        if not first_name and not last_name:
            return Response(
                "No search parameters found.", status=status.HTTP_400_BAD_REQUEST
            )
        result = Family.objects
        if parent_only:
            if first_name:
                result = result.filter(parent__first_name__iexact=first_name)
            if last_name:
                result = result.filter(parent__last_name__iexact=last_name)
        else:
            if first_name:
                result = result.filter(students__first_name__iexact=first_name)
            if last_name:
                result = result.filter(students__last_name__iexact=last_name)

        return Response(FamilySearchSerializer(result.distinct(), many=True).data)


class StudentViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Student.objects.all()
    serializer_class = StudentListSerializer
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]


class FieldViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]


class ExportFamiliesView(APIView):
    queryset = Family.objects.all()
    renderer_classes = [r.CSVRenderer]

    def get(self, request, format=None):
        return Response(list(Family.objects.values()))


class ExportStudentsView(APIView):
    queryset = Student.objects.all()
    renderer_classes = [r.CSVRenderer]

    def get(self, request, format=None):
        return Response(list(Student.objects.values()))


class ExportFieldsView(APIView):
    queryset = Field.objects.all()
    renderer_classes = [r.CSVRenderer]

    def get(self, request, format=None):
        return Response(list(Field.objects.values()))
