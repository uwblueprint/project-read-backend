from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FamilyViewSet, FieldViewSet

router = DefaultRouter()
router.register(r"families", FamilyViewSet, basename="families")
router.register(r"fields", FieldViewSet, basename="fields")

urlpatterns = [
    path("", include(router.urls)),
]
