from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SessionViewSet,
    ClassViewSet,
    EnrolmentViewSet,
    ExportClassesView,
    ExportAttendancesView,
    ExportEnrolmentsView,
    ExportSessionsView,
)

router = DefaultRouter()
router.register(r"sessions", SessionViewSet)
router.register(r"classes", ClassViewSet)
router.register(r"enrolments", EnrolmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("export/classes", ExportClassesView.as_view(), name="export-classes"),
    path(
        "export/attendances", ExportAttendancesView.as_view(), name="export-attendances"
    ),
    path("export/enrolments", ExportEnrolmentsView.as_view(), name="export-enrolments"),
    path("export/sessions", ExportSessionsView.as_view(), name="export-sessions"),
]
