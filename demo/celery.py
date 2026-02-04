"""Celery 配置模块

配置 Celery 应用，设置 broker、任务序列化、时区等。
"""

import os
from celery import Celery

# 设置Django settings模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")

app = Celery("demo")

# 从Django settings加载配置
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自动发现任务
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """调试任务"""
    print(f"Request: {self.request!r}")
