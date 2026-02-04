"""Demo 项目包

确保 Django 启动时 Celery 应用被正确加载。
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
