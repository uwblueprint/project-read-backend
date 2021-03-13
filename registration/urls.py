from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FamilyViewSet

router = DefaultRouter()
router.register(r"families", FamilyViewSet, basename="families")
# router.register(r"students", StudentViewSet, basename="students")

urlpatterns = [
    path("", include(router.urls)),
]
