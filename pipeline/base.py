"""
Pipeline基类模块
定义Pipeline步骤的基础接口
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class PipelineStep(ABC):
    """Pipeline步骤基类"""

    def __init__(self, name: str):
        """
        初始化Pipeline步骤

        Args:
            name: 步骤名称
        """
        self.name = name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行步骤

        Args:
            context: 上下文数据,包含前面步骤的输出

        Returns:
            步骤执行结果,会被合并到context中

        Raises:
            Exception: 执行失败时抛出异常
        """
        pass

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行步骤(包含日志和计时)

        Args:
            context: 上下文数据

        Returns:
            更新后的上下文数据
        """
        print(f"\n步骤: {self.name}")
        print("-" * 60)

        self.start_time = datetime.now()
        try:
            result = self.execute(context)
            self.end_time = datetime.now()
            elapsed = (self.end_time - self.start_time).total_seconds()

            print(f"✓ {self.name}完成 (耗时: {elapsed:.2f}秒)")

            # 合并结果到context
            context.update(result)
            return context

        except Exception as e:
            self.end_time = datetime.now()
            print(f"✗ {self.name}失败: {e}")
            raise
