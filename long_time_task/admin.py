"""Admin 管理模块

提供任务管理界面，支持只读查看、状态筛选等功能。
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import LongTimeTask, TaskState


@admin.register(LongTimeTask)
class LongTimeTaskAdmin(admin.ModelAdmin):
    """长耗时任务管理"""

    list_display = [
        "id",
        "task_type",
        "state_display",
        "create_at",
        "start_at",
        "finish_at",
    ]

    list_filter = [
        "state",
        "task_type",
        "create_at",
    ]

    search_fields = [
        "id",
        "celery_task_id",
        "task_type",
    ]

    readonly_fields = [
        "id",
        "celery_task_id",
        "task_type",
        "task_params",
        "state",
        "result",
        "create_at",
        "start_at",
        "finish_at",
        "error_message",
    ]

    ordering = ["-create_at"]

    list_per_page = 50

    date_hierarchy = "create_at"

    fieldsets = (
        ("基本信息", {"fields": ("id", "celery_task_id", "task_type", "task_params")}),
        ("状态信息", {"fields": ("state",)}),
        ("时间信息", {"fields": ("create_at", "start_at", "finish_at")}),
        ("结果信息", {"fields": ("result", "error_message"), "classes": ("collapse",)}),
    )

    def state_display(self, obj):
        """状态显示"""
        colors = {
            TaskState.PENDING: "#ffc107",  # 黄色
            TaskState.RUNNING: "#17a2b8",  # 蓝色
            TaskState.FINISHED: "#28a745",  # 绿色
            TaskState.FAILED: "#dc3545",  # 红色
        }
        color = colors.get(obj.state, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_state_display(),
        )

    state_display.short_description = "状态"
    state_display.admin_order_field = "state"

    def has_add_permission(self, request):
        """禁止在Admin中添加任务"""
        return False

    def has_delete_permission(self, request, obj=None):
        """禁止在Admin中删除任务"""
        return False

    def has_change_permission(self, request, obj=None):
        """禁止在Admin中修改任务"""
        return False
