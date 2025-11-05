"""
Pipeline模块 - 定义处理流程的各个独立步骤
每个步骤都是独立的类,可以单独使用或组合使用
"""

# 导出基类
from .base import PipelineStep

# 导出工厂函数
from .factory import (
    create_full_pipeline,
    create_summary_only_pipeline,
)

# 导出管理器
from .manager import Pipeline

# 导出步骤类
from .steps import (
    MarkdownGenerateStep,
    MinerUParseStep,
    PDFUploadStep,
    SaveSummaryStep,
    SummaryGenerateStep,
)

__all__ = [
    # 基类
    "PipelineStep",
    # 步骤类
    "PDFUploadStep",
    "MinerUParseStep",
    "MarkdownGenerateStep",
    "SummaryGenerateStep",
    "SaveSummaryStep",
    # 管理器
    "Pipeline",
    # 工厂函数
    "create_full_pipeline",
    "create_summary_only_pipeline",
]
