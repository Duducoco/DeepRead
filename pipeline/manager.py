"""
Pipeline管理器
管理和执行多个步骤
"""

from datetime import datetime
from typing import Any, Dict, Optional

from .base import PipelineStep


class Pipeline:
    """Pipeline管理器 - 管理和执行多个步骤"""

    def __init__(self, name: str = "PDF处理流程"):
        """
        初始化Pipeline

        Args:
            name: Pipeline名称
        """
        self.name = name
        self.steps: list[PipelineStep] = []
        self.context: Dict[str, Any] = {}

    def add_step(self, step: PipelineStep) -> "Pipeline":
        """
        添加步骤

        Args:
            step: Pipeline步骤

        Returns:
            self,用于链式调用
        """
        self.steps.append(step)
        return self

    def run(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        运行整个Pipeline

        Args:
            initial_context: 初始上下文数据

        Returns:
            最终的上下文数据

        Raises:
            Exception: 任何步骤失败时抛出异常
        """
        print(f"\n{'=' * 60}")
        print(f"{self.name}")
        print(f"{'=' * 60}")

        # 初始化context
        self.context = initial_context or {}
        self.context["pipeline_start_time"] = datetime.now()

        # 逐步执行
        for i, step in enumerate(self.steps, 1):
            self.context["current_step"] = i
            self.context["total_steps"] = len(self.steps)
            self.context = step.run(self.context)

        # 记录完成时间
        self.context["pipeline_end_time"] = datetime.now()
        elapsed = (
            self.context["pipeline_end_time"] - self.context["pipeline_start_time"]
        ).total_seconds()

        print(f"\n{'=' * 60}")
        print(f"{self.name}完成! (总耗时: {elapsed:.2f}秒)")
        print(f"{'=' * 60}\n")

        return self.context
