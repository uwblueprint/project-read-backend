from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImportView

from .views import SessionViewSet, ClassViewSet, EnrolmentViewSet

router = DefaultRouter()
router.register(r"sessions", SessionViewSet)
router.register(r"classes", ClassViewSet)
router.register(r"enrolments", EnrolmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("import/", ImportView.as_view(), name="import"),
]
