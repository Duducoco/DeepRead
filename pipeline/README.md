# Pipeline模块

Pipeline模块提供了模块化的PDF处理流程架构。

## 模块结构

```
pipeline/
├── __init__.py      # 模块导出
├── base.py          # PipelineStep基类
├── steps.py         # 所有步骤类
├── manager.py       # Pipeline管理器
└── factory.py       # 预定义流程工厂函数
```

## 文件说明

### base.py
定义了`PipelineStep`抽象基类,所有步骤都继承自这个基类。

### steps.py
包含所有具体的步骤类:
- `PDFParseStep` - PDF解析步骤
- `GiteeUploadStep` - Gitee上传步骤
- `MarkdownGenerateStep` - Markdown获取步骤
- `SummaryGenerateStep` - 总结生成步骤
- `SaveSummaryStep` - 保存总结步骤

### manager.py
包含`Pipeline`类,用于管理和执行多个步骤。

### factory.py
提供预定义的Pipeline工厂函数:
- `create_full_pipeline()` - 完整流程(含Gitee)
- `create_local_pipeline()` - 本地流程(不含Gitee)
- `create_summary_only_pipeline()` - 仅总结流程

## 使用示例

### 导入模块

```python
# 导入所有类和函数
from pipeline import (
    Pipeline,
    PipelineStep,
    PDFParseStep,
    GiteeUploadStep,
    MarkdownGenerateStep,
    SummaryGenerateStep,
    SaveSummaryStep,
    create_full_pipeline,
    create_local_pipeline,
    create_summary_only_pipeline,
)
```

### 使用预定义流程

```python
from pipeline import create_local_pipeline

# 创建本地处理流程
pipeline = create_local_pipeline()

# 运行流程
context = {"pdf_path": "document.pdf"}
result = pipeline.run(context)
```

### 自定义流程

```python
from pipeline import Pipeline, PDFParseStep, SummaryGenerateStep, SaveSummaryStep

# 创建自定义流程
pipeline = Pipeline("我的流程")
pipeline.add_step(PDFParseStep())
pipeline.add_step(SummaryGenerateStep())
pipeline.add_step(SaveSummaryStep())

# 运行流程
context = {"pdf_path": "document.pdf"}
result = pipeline.run(context)
```

### 单独使用步骤

```python
from pipeline import PDFParseStep

# 创建步骤
step = PDFParseStep()

# 运行步骤
context = {"pdf_path": "document.pdf"}
result = step.run(context)
```

## 设计优势

1. **模块化** - 每个文件职责单一,易于维护
2. **可扩展** - 添加新步骤只需在steps.py中添加新类
3. **清晰** - 文件结构清晰,一目了然
4. **灵活** - 可以单独使用步骤,也可以组合使用
