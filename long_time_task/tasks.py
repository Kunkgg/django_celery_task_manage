"""Celery 任务模块入口

Celery Worker 自动发现任务时加载此模块。
此文件仅用于触发任务定义模块的导入，确保任务注册表被正确初始化。

注意：实际的 Celery 任务定义在 celery_tasks.py 中。
此文件的存在是为了配合 Celery 的 autodiscover_tasks() 功能。
"""

# 导入任务定义模块，触发任务注册
# noqa: F401 - 导入 tasks_definitions 是为了触发模块加载以注册任务
from . import tasks_definitions  # noqa: F401

# 导入 Celery 任务处理器，确保它被 Worker 发现
from .celery_tasks import execute_long_time_task

__all__ = ["execute_long_time_task"]
