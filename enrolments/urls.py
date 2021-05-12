from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SessionViewSet, ClassViewSet

router = DefaultRouter()
router.register(r"sessions", SessionViewSet)
router.register(r"classes", ClassViewSet)

urlpatterns = [path("", include(router.urls))]
