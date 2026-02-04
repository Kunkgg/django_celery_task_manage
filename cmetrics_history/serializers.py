from rest_framework import serializers
from .models import CmetricsHistory


class CmetricsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CmetricsHistory
        fields = [
            "id",
            "search_version",
            "source_type",
            "product",
            "lan",
            "group_name",
            "data_type",
            "data_source",
            "project_name",
            "project_real_name",
            "build_no",
            "build_url",
            "commit_id",
            "b_version",
            "remark",
            "kind",
            "keep",
            "is_active",
            "detail_url",
            "create_at",
        ]
