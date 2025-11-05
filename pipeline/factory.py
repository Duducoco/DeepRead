"""
Pipeline工厂函数
提供预定义的Pipeline配置
"""

from .manager import Pipeline
from .steps import (
    MarkdownGenerateStep,
    MinerUParseStep,
    PDFUploadStep,
    SaveSummaryStep,
    SummaryGenerateStep,
)


def create_full_pipeline() -> Pipeline:
    """
    创建完整的PDF处理流程(通过Gitee)
    PDF → 上传Gitee → MinerU解析URL → 生成总结 → 保存

    Returns:
        配置好的Pipeline
    """
    pipeline = Pipeline("完整PDF处理流程")
    pipeline.add_step(PDFUploadStep())  # 上传PDF到Gitee
    pipeline.add_step(MinerUParseStep())  # 使用Gitee URL解析
    pipeline.add_step(SummaryGenerateStep())  # 生成总结
    pipeline.add_step(SaveSummaryStep())  # 保存结果
    return pipeline


def create_summary_only_pipeline() -> Pipeline:
    """
    创建仅总结流程(从已有Markdown生成总结)
    Markdown → 生成总结 → 保存

    Returns:
        配置好的Pipeline
    """
    pipeline = Pipeline("Markdown总结流程")
    pipeline.add_step(MarkdownGenerateStep())
    pipeline.add_step(SummaryGenerateStep())
    pipeline.add_step(SaveSummaryStep())
    return pipeline
