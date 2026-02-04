"""Celery 任务模块

定义 Celery 任务处理函数，包括任务执行、错误处理和状态更新。
"""

import json
import logging
import traceback
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.utils import timezone

from .models import LongTimeTask, TaskState
from .registry import LongTimeTaskRegister

logger = logging.getLogger(__name__)


def _debug_log_task_registry():
    """调试日志：记录当前进程中的任务注册表"""
    all_tasks = LongTimeTaskRegister.get_all_tasks()
    logger.info(f"[DEBUG] 当前已注册的任务: {list(all_tasks.keys())}")
    return all_tasks


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
)
def execute_long_time_task(self, task_id: int):
    """
    执行长耗时任务的Celery任务

    Args:
        task_id: LongTimeTask模型的ID
    """
    try:
        # 获取任务记录
        task = LongTimeTask.objects.get(id=task_id)

        # 更新任务状态为运行中
        task.state = TaskState.RUNNING
        task.start_at = timezone.now()
        task.celery_task_id = self.request.id
        task.save(update_fields=["state", "start_at", "celery_task_id"])

        # 获取任务配置
        # 调试日志：查看任务注册表状态
        all_tasks = _debug_log_task_registry()
        logger.info(f"[DEBUG] 正在查找任务类型: {task.task_type}")
        logger.info(f"[DEBUG] 任务注册表内容: {all_tasks}")
        
        task_config = LongTimeTaskRegister.get_task(task.task_type)
        logger.info(f"[DEBUG] 获取到的任务配置: {task_config}")
        
        if not task_config:
            logger.error(f"[DEBUG] 任务类型 '{task.task_type}' 未在注册表中找到！")
            raise ValueError(f"Unknown task type: {task.task_type}")

        # 解析任务参数
        params = json.loads(task.task_params)

        # 执行任务处理函数
        logger.info(f"Executing task {task_id}: {task.task_type}")
        result = task_config.handler(task_id, params)

        # 更新任务状态为完成
        task.state = TaskState.FINISHED
        task.finish_at = timezone.now()
        task.result = json.dumps(result, ensure_ascii=False)
        task.save(update_fields=["state", "finish_at", "result"])

        logger.info(f"Task {task_id} completed successfully")
        return {"task_id": task_id, "status": "success"}

    except SoftTimeLimitExceeded:
        # 软超时处理
        logger.warning(f"Task {task_id} soft time limit exceeded")
        _mark_task_failed(task_id, "Task execution time limit exceeded")
        raise

    except Exception as e:
        # 判断是否可重试
        try:
            task = LongTimeTask.objects.get(id=task_id)
            task_config = LongTimeTaskRegister.get_task(task.task_type)

            retryable = task_config and LongTimeTaskRegister.is_retryable(
                task.task_type, e
            )
            if retryable:
                # 可重试异常，让Celery处理重试
                msg = f"Task {task_id} failed with retryable error: {e}"
                logger.warning(msg)
                if self.request.retries < task_config.max_retries:
                    raise self.retry(exc=e, countdown=task_config.retry_delay)
        except LongTimeTask.DoesNotExist:
            pass

        # 不可重试或已达最大重试次数，标记为失败
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        _mark_task_failed(task_id, error_msg)
        logger.error(f"Task {task_id} failed: {error_msg}")
        return {"task_id": task_id, "status": "failed", "error": str(e)}


def _mark_task_failed(task_id: int, error_message: str):
    """标记任务为失败状态"""
    try:
        task = LongTimeTask.objects.get(id=task_id)
        task.state = TaskState.FAILED
        task.finish_at = timezone.now()
        task.error_message = error_message
        task.save(update_fields=["state", "finish_at", "error_message"])
    except LongTimeTask.DoesNotExist:
        logger.error(f"Task {task_id} not found when marking as failed")
