"""任务定义模块

示例任务定义，展示如何注册长耗时任务。
"""

import time
import random
from .registry import LongTimeTaskRegister


@LongTimeTaskRegister.register(
    task_type="data_analysis",
    description="数据分析任务",
    timeout=7200,
    soft_timeout=6900,
    max_retries=3,
    queue="heavy",
    param_schema={
        "required": ["dataset_id"],
        "properties": {
            "dataset_id": {"type": "integer"},
            "analysis_type": {"type": "string"},
        },
    },
)
def analyze_data(task_id: int, params: dict) -> dict:
    """数据分析任务处理函数"""
    dataset_id = params.get("dataset_id")
    analysis_type = params.get("analysis_type", "basic")

    # 模拟耗时操作
    time.sleep(5)

    # 返回结果
    return {
        "dataset_id": dataset_id,
        "analysis_type": analysis_type,
        "result": "analysis_complete",
        "summary": {
            "total_records": random.randint(1000, 10000),
            "avg_value": round(random.random() * 100, 2),
        },
    }


@LongTimeTaskRegister.register(
    task_type="file_processing",
    description="文件处理任务",
    timeout=3600,
    queue="default",
    param_schema={
        "required": ["file_path"],
        "properties": {
            "file_path": {"type": "string"},
            "output_format": {"type": "string"},
        },
    },
)
def process_file(task_id: int, params: dict) -> dict:
    """文件处理任务"""
    file_path = params.get("file_path")
    output_format = params.get("output_format", "json")

    # 模拟耗时操作
    time.sleep(3)

    return {
        "input_file": file_path,
        "output_format": output_format,
        "output_file": f"/results/{task_id}.{output_format}",
        "processed": True,
    }


@LongTimeTaskRegister.register(
    task_type="report_generation",
    description="报告生成任务",
    timeout=1800,
    queue="default",
    priority=7,
)
def generate_report(task_id: int, params: dict) -> dict:
    """报告生成任务"""
    report_type = params.get("report_type", "summary")

    # 模拟耗时操作
    time.sleep(2)

    return {
        "report_type": report_type,
        "report_path": f"/reports/{task_id}.pdf",
        "pages": random.randint(5, 50),
    }
