"""任务注册器模块

提供 LongTimeTaskRegister 单例类，用于注册和管理长耗时任务。
支持装饰器方式和手动注册方式注册任务。
"""

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class TaskConfig:
    """任务配置"""

    name: str  # 任务名称
    handler: Callable  # 处理函数
    description: str = ""  # 任务描述
    timeout: int = 3600  # 超时时间(秒)
    soft_timeout: int = 3300  # 软超时时间(秒)
    max_retries: int = 3  # 最大重试次数
    retry_delay: int = 60  # 重试延迟(秒)
    retry_backoff: bool = True  # 是否使用指数退避
    retry_backoff_max: int = 600  # 最大退避时间(秒)
    queue: str = "default"  # 任务队列
    priority: int = 5  # 优先级 (1-10, 10最高)
    param_schema: Optional[Dict] = None  # 参数验证schema
    retryable_exceptions: tuple = field(  # 可重试的异常类型
        default_factory=lambda: (ConnectionError, TimeoutError)
    )


class LongTimeTaskRegister:
    """长耗时任务注册器 - 单例模式"""

    _instance = None
    _tasks: Dict[str, TaskConfig] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(
        cls,
        task_type: str,
        description: str = "",
        timeout: int = 3600,
        soft_timeout: int = 3300,
        max_retries: int = 3,
        retry_delay: int = 60,
        retry_backoff: bool = True,
        retry_backoff_max: int = 600,
        queue: str = "default",
        priority: int = 5,
        param_schema: Optional[Dict] = None,
        retryable_exceptions: tuple = (ConnectionError, TimeoutError),
    ):
        """
        装饰器方式注册任务

        使用示例:
        @LongTimeTaskRegister.register(
            task_type='data_analysis',
            description='数据分析任务',
            timeout=7200,
            queue='heavy'
        )
        def analyze_data(task_id: int, params: dict) -> dict:
            # 任务处理逻辑
            return {'status': 'success', 'data': result}
        """

        def decorator(func: Callable):
            config = TaskConfig(
                name=task_type,
                handler=func,
                description=description,
                timeout=timeout,
                soft_timeout=soft_timeout,
                max_retries=max_retries,
                retry_delay=retry_delay,
                retry_backoff=retry_backoff,
                retry_backoff_max=retry_backoff_max,
                queue=queue,
                priority=priority,
                param_schema=param_schema,
                retryable_exceptions=retryable_exceptions,
            )
            cls._tasks[task_type] = config
            logger.info(f"Registered task: {task_type}")

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def get_task(cls, task_type: str) -> Optional[TaskConfig]:
        """获取任务配置"""
        return cls._tasks.get(task_type)

    @classmethod
    def get_all_tasks(cls) -> Dict[str, TaskConfig]:
        """获取所有注册的任务"""
        return cls._tasks.copy()

    @classmethod
    def validate_params(cls, task_type: str, params: dict) -> bool:
        """验证任务参数"""
        config = cls.get_task(task_type)
        if not config:
            raise ValueError(f"Unknown task type: {task_type}")

        if config.param_schema:
            required = config.param_schema.get("required", [])
            for req_field in required:
                if req_field not in params:
                    raise ValueError(f"Missing required param: {req_field}")
        return True

    @classmethod
    def is_retryable(cls, task_type: str, exception: Exception) -> bool:
        """判断异常是否可重试"""
        config = cls.get_task(task_type)
        if not config:
            return False
        return isinstance(exception, config.retryable_exceptions)
