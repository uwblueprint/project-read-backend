from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FamilyViewSet,
    FieldViewSet,
    ExportFamiliesView,
    ExportFieldsView,
    ExportStudentsView,
)

router = DefaultRouter()
router.register(r"families", FamilyViewSet)
router.register(r"fields", FieldViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("export/families", ExportFamiliesView.as_view(), name="export-families"),
    path("export/students", ExportStudentsView.as_view(), name="export-students"),
    path("export/fields", ExportFieldsView.as_view(), name="export-fields"),
]
