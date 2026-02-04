from django.db import models


# Create your models here.
class CmetricsHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    search_version = models.CharField(max_length=50)
    source_type = models.CharField(max_length=50)
    product = models.CharField(max_length=100)
    lan = models.CharField(max_length=10)
    group_name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50)
    data_source = models.CharField(max_length=100)
    project_name = models.CharField(max_length=100)
    project_real_name = models.CharField(max_length=200)
    build_no = models.CharField(max_length=50)
    build_url = models.URLField()
    commit_id = models.CharField(max_length=100)
    b_version = models.CharField(max_length=50)
    remark = models.TextField()
    kind = models.CharField(max_length=50)
    keep = models.BooleanField()
    is_active = models.BooleanField()
    detail_url = models.URLField()
    create_at = models.DateTimeField(auto_now_add=True)
