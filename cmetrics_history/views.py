from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from .models import CmetricsHistory
from .serializers import CmetricsHistorySerializer


class CmetricsHistoryPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class CmetricsHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API 端点用于查看 Cmetrics 历史数据
    """

    queryset = CmetricsHistory.objects.filter(is_active=True).order_by("-create_at")
    serializer_class = CmetricsHistorySerializer
    pagination_class = CmetricsHistoryPagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "search_version",
        "source_type",
        "product",
        "lan",
        "group_name",
        "data_type",
    ]
