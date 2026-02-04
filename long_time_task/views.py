"""API 视图模块

提供任务提交、查询等 REST API 接口。
"""

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator

from .models import LongTimeTask, TaskState
from .registry import LongTimeTaskRegister
from .celery_tasks import execute_long_time_task

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class TaskSubmitView(View):
    """任务提交API"""

    def post(self, request):
        """
        提交新任务

        Request Body:
        {
            "task_type": "data_analysis",
            "params": {"dataset_id": 123}
        }

        Response:
        {
            "success": true,
            "task_id": 1,
            "message": "Task submitted successfully"
        }
        """
        try:
            data = json.loads(request.body)
            task_type = data.get("task_type")
            params = data.get("params", {})

            # 验证任务类型
            task_config = LongTimeTaskRegister.get_task(task_type)
            if not task_config:
                return JsonResponse(
                    {"success": False, "error": f"Unknown task type: {task_type}"},
                    status=400,
                )

            # 验证参数
            try:
                LongTimeTaskRegister.validate_params(task_type, params)
            except ValueError as e:
                return JsonResponse({"success": False, "error": str(e)}, status=400)

            # 创建任务记录
            task = LongTimeTask.objects.create(
                task_type=task_type,
                task_params=json.dumps(params, ensure_ascii=False),
                state=TaskState.PENDING,
                celery_task_id="",  # 稍后由Celery填充
            )

            # 提交到Celery队列
            celery_task = execute_long_time_task.apply_async(
                args=[task.id],
                queue=task_config.queue,
                priority=task_config.priority,
            )

            # 更新Celery任务ID
            task.celery_task_id = celery_task.id
            task.save(update_fields=["celery_task_id"])

            logger.info(f"Task {task.id} submitted: {task_type}")

            return JsonResponse(
                {
                    "success": True,
                    "task_id": task.id,
                    "message": "Task submitted successfully",
                }
            )

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.exception("Error submitting task")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class TaskDetailView(View):
    """任务详情API"""

    def get(self, request, task_id):
        """
        获取任务详情

        Response:
        {
            "success": true,
            "task": {
                "id": 1,
                "task_type": "data_analysis",
                "state": "FINISHED",
                "result": {...},
                "create_at": "2024-01-01T10:00:00Z",
                "start_at": "2024-01-01T10:00:01Z",
                "finish_at": "2024-01-01T10:05:00Z"
            }
        }
        """
        try:
            task = LongTimeTask.objects.get(id=task_id)

            task_data = {
                "id": task.id,
                "task_type": task.task_type,
                "state": task.state,
                "create_at": task.create_at.isoformat() if task.create_at else None,
                "start_at": task.start_at.isoformat() if task.start_at else None,
                "finish_at": task.finish_at.isoformat() if task.finish_at else None,
            }

            # 只有完成或失败时才返回结果/错误信息
            if task.state == TaskState.FINISHED:
                task_data["result"] = json.loads(task.result) if task.result else None
            elif task.state == TaskState.FAILED:
                task_data["error_message"] = task.error_message

            return JsonResponse({"success": True, "task": task_data})

        except LongTimeTask.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Task not found"}, status=404
            )


class TaskListView(View):
    """任务列表API"""

    def get(self, request):
        """
        获取任务列表

        Query Parameters:
        - state: 按状态筛选 (PENDING/RUNNING/FINISHED/FAILED)
        - task_type: 按任务类型筛选
        - page: 页码 (默认1)
        - page_size: 每页数量 (默认20, 最大100)

        Response:
        {
            "success": true,
            "tasks": [...],
            "total": 100,
            "page": 1,
            "page_size": 20,
            "total_pages": 5
        }
        """
        queryset = LongTimeTask.objects.all()

        # 筛选条件
        state = request.GET.get("state")
        if state and state in TaskState.values:
            queryset = queryset.filter(state=state)

        task_type = request.GET.get("task_type")
        if task_type:
            queryset = queryset.filter(task_type=task_type)

        # 分页
        page = int(request.GET.get("page", 1))
        page_size = min(int(request.GET.get("page_size", 20)), 100)

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        tasks = [
            {
                "id": task.id,
                "task_type": task.task_type,
                "state": task.state,
                "create_at": task.create_at.isoformat() if task.create_at else None,
                "finish_at": task.finish_at.isoformat() if task.finish_at else None,
            }
            for task in page_obj
        ]

        return JsonResponse(
            {
                "success": True,
                "tasks": tasks,
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class TaskTypeListView(View):
    """任务类型列表API"""

    def get(self, request):
        """
        获取所有已注册的任务类型

        Response:
        {
            "code": 0,
            "message": "success",
            "data": {
                "task_types": [
                    {
                        "name": "data_analysis",
                        "description": "数据分析任务",
                        "timeout": 7200,
                        "queue": "heavy"
                    }
                ]
            }
        }
        """
        try:
            all_tasks = LongTimeTaskRegister.get_all_tasks()

            task_types = []
            for task_type, config in all_tasks.items():
                task_types.append({
                    "name": task_type,
                    "description": config.description,
                    "timeout": config.timeout,
                    "soft_timeout": config.soft_timeout,
                    "max_retries": config.max_retries,
                    "queue": config.queue,
                    "priority": config.priority,
                })

            return JsonResponse({
                "code": 0,
                "message": "success",
                "data": {
                    "task_types": task_types
                }
            })

        except Exception as e:
            logger.exception("Error getting task types")
            return JsonResponse({
                "code": 500,
                "message": str(e),
                "data": {
                    "task_types": []
                }
            }, status=500)
