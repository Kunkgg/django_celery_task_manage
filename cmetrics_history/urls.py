from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CmetricsHistoryViewSet

router = DefaultRouter()
router.register(
    r"cmetrics-history", CmetricsHistoryViewSet, basename="cmetrics-history"
)

urlpatterns = [
    path("", include(router.urls)),
]
