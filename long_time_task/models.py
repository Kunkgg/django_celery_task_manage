from django.db import models


class TaskState(models.TextChoices):
    """任务状态枚举"""

    PENDING = "PENDING", "等待执行"
    RUNNING = "RUNNING", "正在执行"
    FINISHED = "FINISHED", "已完成"
    FAILED = "FAILED", "执行失败"


class LongTimeTask(models.Model):
    """长耗时任务模型"""

    # 主键使用自增ID
    id = models.BigAutoField(primary_key=True)

    # Celery任务ID
    celery_task_id = models.CharField(
        max_length=255,
        default="",
        blank=True,
        db_index=True,
        verbose_name="Celery任务ID",
    )

    # 任务类型 - 对应注册器中的任务标识符
    task_type = models.CharField(max_length=100, db_index=True, verbose_name="任务类型")

    # 任务参数 - JSON格式存储
    task_params = models.TextField(default="{}", verbose_name="任务参数")

    # 任务状态
    state = models.CharField(
        max_length=20,
        choices=TaskState.choices,
        default=TaskState.PENDING,
        db_index=True,
        verbose_name="任务状态",
    )

    # 任务结果 - JSON格式或文件路径
    result = models.TextField(null=True, blank=True, verbose_name="任务结果")

    # 时间字段
    create_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name="创建时间"
    )
    start_at = models.DateTimeField(null=True, blank=True, verbose_name="开始执行时间")
    finish_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")

    # 错误信息
    error_message = models.TextField(null=True, blank=True, verbose_name="错误信息")

    class Meta:
        db_table = "long_time_task"
        verbose_name = "长耗时任务"
        verbose_name_plural = "长耗时任务"
        ordering = ["-create_at"]
        indexes = [
            models.Index(fields=["state", "create_at"]),
            models.Index(fields=["task_type", "state"]),
        ]

    def __str__(self):
        return f"{self.task_type}#{self.id} - {self.state}"
