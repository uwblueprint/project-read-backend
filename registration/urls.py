from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FamilyViewSet, FieldViewSet

router = DefaultRouter()
router.register(r"families", FamilyViewSet)
router.register(r"fields", FieldViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
