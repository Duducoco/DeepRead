# DeepRead - PDF智能总结工具

一个强大的PDF智能分析工具,使用Gitee存储PDF,MinerU的API解析PDF为markdown,然后调用Claude大模型生成高质量的文档总结。

## 功能特点

- **Gitee云存储**: 自动将PDF上传到Gitee仓库,永久保存并可分享
- **高精度PDF解析**: 使用MinerU云服务解析PDF,支持复杂文档结构，自动下载并解压解析结果
- **智能AI总结**: 集成Anthropic Claude,提供多种总结风格

## 系统要求

- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv) - 快速的Python包管理器
- Gitee账号和访问令牌 (从 [gitee.com](https://gitee.com) 获取)
- MinerU API密钥 (从 [mineru.net](https://mineru.net) 获取)
- Anthropic API密钥 (从 [anthropic.com](https://www.anthropic.com) 获取)

## 安装步骤

### 0. 安装uv

如果还没有安装uv,请先安装:

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 1. 克隆或下载项目

```bash
git clone https://github.com/Duducoco/DeepRead.git
cd DeepRead
```

### 2. 使用uv创建虚拟环境并安装依赖

```bash
# 创建虚拟环境并安装依赖(一步完成)
uv sync
```

### 3. 配置API密钥

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

编辑`.env`文件,填入你的API密钥:

```env
# Gitee配置(PDF存储)
GITEE_ACCESS_TOKEN=your_gitee_access_token_here
GITEE_OWNER=your_gitee_username
GITEE_REPO=your_repo_name
GITEE_BRANCH=master
GITEE_UPLOAD_PATH=pdfs/

# MinerU API配置
MINERU_API_KEY=your_mineru_api_key_here
MINERU_API_URL=https://mineru.net/api/v4/extract/task

# Anthropic Claude API配置
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 可选: Claude中转API地址(如果使用中转API)
# 如果使用官方API,注释掉或删除此行
# ANTHROPIC_BASE_URL=https://your-proxy-api.com/v1

# 可选: 模型配置
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 配置说明

#### 1. Gitee配置(必需)

**获取Gitee访问令牌:**
1. 登录 [Gitee](https://gitee.com)
2. 进入 设置 → 私人令牌 → 生成新令牌
3. 勾选 `projects` 权限
4. 生成并复制令牌到`.env`文件

**创建存储仓库:**
1. 在Gitee创建一个新仓库(如: `pdf-storage`)
2. 仓库需要设置为**公开**
3. 将仓库名和用户名填入`.env`文件

**参数说明:**
- `GITEE_ACCESS_TOKEN`: Gitee私人访问令牌
- `GITEE_OWNER`: 你的Gitee用户名
- `GITEE_REPO`: 存储PDF的仓库名
- `GITEE_BRANCH`: 分支名(默认master)
- `GITEE_UPLOAD_PATH`: PDF存储路径前缀(默认pdfs/)

#### 2. MinerU和Claude配置

按照原有说明配置MinerU和Claude的API密钥。

**关于中转API:**
如果你在国内访问Claude API遇到困难,可以使用中转API服务。只需在`.env`文件中设置`ANTHROPIC_BASE_URL`为你的中转API地址即可。

## 使用方法

### 基本用法

使用uv运行DeepRead:

```bash
# 直接使用uv run(推荐,无需激活虚拟环境)
uv run python main.py --input document.pdf

# 或者激活虚拟环境后运行
# Windows
.venv\Scripts\activate
python main.py --input document.pdf

# macOS/Linux
source .venv/bin/activate
python main.py --input document.pdf
```

### 选择总结风格

```bash
uv run python main.py --input document.pdf --style detailed
```

支持的总结风格:
<!-- - `concise` - 简洁模式: 3-5段简要总结 -->

- `detailed` - 详细模式: 全面深入的分析(默认)
<!-- - `bullet` - 要点模式: 分层级的要点列表 -->
<!-- - `academic` - 学术模式: 符合学术规范的总结 -->
<!-- - `casual` - 轻松模式: 易懂的日常语言 -->

### 保存原始Markdown

MinerU解析的原始markdown文件会自动保存在output的文件夹中（`output/时间戳_文件名/full.md`）。

### 自定义提示词

使用自定义的总结提示词:

```bash
uv run python main.py --input document.pdf --prompt "请用5个要点总结这个文档的关键内容"
```

### 查看配置

检查当前的配置信息:

```bash
uv run python main.py --config
```

## 项目结构

```
DeepRead/
├── .env                    # 环境变量配置(需要自己创建)
├── .env.example           # 环境变量模板
├── .gitignore             # Git忽略文件
├── pyproject.toml         # 项目配置和依赖(uv)
├── uv.lock                # 依赖锁定文件(uv自动生成)
├── README.md              # 项目文档(本文件)
├── config.py              # 配置管理模块
├── main.py                # 命令行入口
├── pipeline/              # Pipeline处理模块
│   ├── __init__.py        # 模块导出
│   ├── base.py            # Pipeline基类定义
│   ├── steps.py           # 各个处理步骤(上传/解析/总结)
│   ├── manager.py         # Pipeline管理器
│   ├── factory.py         # Pipeline工厂函数
│   └── README.md          # Pipeline模块文档
├── prompts/               # 提示词模板目录
│   └── detailed.md        # 详细总结提示词模板
├── examples/              # 示例PDF文件目录
│   ├── example.pdf        # 示例PDF文件
│   └── ...                # 其他示例文件
└── output/                # 默认输出目录
    └── 时间戳_文件名/     # 解析后的文件夹
        ├── full.md        # MinerU解析的完整markdown
        ├── summary.md     # AI生成的智能总结
        └── ...            # 其他解析结果文件(图片、表格等)
```

## 工作流程

DeepRead采用**Pipeline架构**,处理流程清晰可扩展:

### Pipeline架构说明

DeepRead使用模块化的Pipeline设计,每个处理步骤都是独立的类:

- **PipelineStep基类**: 定义统一的步骤接口
- **Pipeline管理器**: 串联多个步骤,管理执行流程
- **工厂函数**: 提供预定义的Pipeline配置

### 完整处理流程

1. **上传PDF到Gitee** (`PDFUploadStep`): 将本地PDF文件上传到Gitee仓库,获取可访问的URL
2. **MinerU解析** (`MinerUParseStep`): 使用Gitee的raw URL调用MinerU API解析PDF为markdown
3. **下载解析结果**: 自动下载解析结果的ZIP包并解压到 `output/时间戳_文件名/` 目录
4. **生成总结** (`SummaryGenerateStep`): 将markdown内容传递给Claude生成智能总结
5. **保存结果** (`SaveSummaryStep`): 保存总结文件到 `output/时间戳_文件名/summary.md`

### 可选流程

如果已有markdown文件,可以跳过解析步骤,直接生成总结:

1. **读取Markdown** (`MarkdownGenerateStep`): 从本地读取markdown文件
2. **生成总结** (`SummaryGenerateStep`): 调用Claude生成总结
3. **保存结果** (`SaveSummaryStep`): 保存总结到指定位置

## 输出文件

处理完成后，会生成以下文件：

### 1. 解析结果目录
`output/时间戳_PDF文件名/`
- `full.md` - MinerU解析的完整markdown文件
- 其他解析相关文件（图片、表格等）

### 2. 总结文件
`output/时间戳_文件名/summary.md` - AI生成的智能总结

## 使用示例

DeepRead提供了一些示例PDF文件供您测试(位于 `examples/` 目录):

### 示例1: 快速测试工具

```bash
# 使用examples目录中的示例文件测试
uv run python main.py --input examples/example.pdf --style detailed
```

### 示例2: 处理学术论文

```bash
# 处理学术论文并生成详细总结
uv run python main.py --input examples/BugGen.pdf --style detailed
```

### 示例3: 使用自定义提示词

```bash
uv run python main.py --input examples/example.pdf --prompt "请用5个要点总结这个文档的关键内容"
```

### 示例4: 处理您自己的PDF

```bash
# 使用相对路径
uv run python main.py --input path/to/your/document.pdf

# 使用绝对路径
uv run python main.py --input D:\Documents\research.pdf
```

## API说明

### Gitee API

Gitee是国内领先的代码托管平台,DeepRead使用Gitee存储PDF文件:
- **云端存储**: PDF文件永久保存在Gitee仓库
- **可访问性**: 生成公开的raw URL供MinerU访问
- **版本控制**: 自动管理文件版本和历史记录
- **便于分享**: 可以通过Gitee链接分享PDF文件

**获取访问令牌:**
1. 访问 [Gitee设置](https://gitee.com/profile/personal_access_tokens)
2. 生成新令牌,勾选 `projects` 权限
3. 复制令牌到`.env`文件

**目录组织:**
PDF文件默认按日期组织: `pdfs/2024/01/{sha of file}.pdf`

### MinerU API

MinerU是一个强大的文档解析工具,能够:
- 识别复杂的PDF布局
- 提取文本、表格、图片等元素
- 转换为结构化的markdown格式
- 支持通过URL解析PDF
- 返回完整的解析结果压缩包

获取API密钥: [https://mineru.net](https://mineru.net)

**API端点**: `https://mineru.net/api/v4/extract/task`

**解析结果**:
- 解析完成后，会返回一个ZIP文件的下载链接
- ZIP文件包含 `full.md` 等解析结果
- 工具会自动下载并解压到 `output/时间戳_文件名/` 目录

### Anthropic Claude API

Claude是Anthropic开发的大语言模型,特点:
- 擅长长文本理解和总结
- 输出质量高、格式规范
- 支持中英文等多种语言

获取API密钥: [https://console.anthropic.com](https://console.anthropic.com)

**使用中转API:**
如果你在国内无法直接访问Anthropic官方API,可以使用中转API服务:
1. 在`.env`文件中设置`ANTHROPIC_BASE_URL`
2. 填入你的中转API服务地址(如: `https://api.example.com/v1`)
3. 确保中转服务与Anthropic官方API兼容
4. 使用中转API时,仍需要有效的`ANTHROPIC_API_KEY`

常见中转API服务包括各种OpenAI兼容的API代理服务。

## 故障排除

### 问题: "配置错误: GITEE_ACCESS_TOKEN未设置"

**解决方案**:
1. 确保已创建`.env`文件
2. 检查Gitee访问令牌是否正确配置
3. 验证令牌具有`projects`权限

### 问题: "上传PDF到Gitee失败"

**解决方案**:
1. 检查Gitee仓库是否存在
2. 确认仓库名和用户名拼写正确
3. 验证访问令牌是否有效

### 问题: "配置错误: MINERU_API_KEY未设置"

**解决方案**: 确保已经创建`.env`文件并正确填入API密钥

### 问题: "文件不存在"

**解决方案**: 检查PDF文件路径是否正确,可以使用绝对路径或相对路径

### 问题: "API请求失败"

**解决方案**:
1. 检查网络连接
2. 确认API密钥有效
3. 检查API配额是否用完

### 问题: 处理大文件超时

**解决方案**: 可以在`.env`中增加超时时间:

```env
REQUEST_TIMEOUT=600  # 增加到10分钟
```

### 问题: 使用中转API时连接失败

**解决方案**:
1. 确认`ANTHROPIC_BASE_URL`格式正确,通常以`/v1`结尾
2. 检查中转API服务是否正常运行
3. 确认中转API的认证方式与Anthropic官方API兼容
4. 尝试使用`--verbose`参数查看详细错误信息

## 高级配置

### 环境变量完整列表

```env
# Gitee配置
GITEE_ACCESS_TOKEN=your_token    # 必需
GITEE_OWNER=your_username        # 必需
GITEE_REPO=your_repo             # 必需
GITEE_BRANCH=master              # 可选,默认master
GITEE_UPLOAD_PATH=pdfs/          # 可选,默认pdfs/

# MinerU配置
MINERU_API_KEY=your_key          # 必需
MINERU_API_URL=https://mineru.net/api/v4/extract/task  # 可选,默认值已设置

# Claude配置
ANTHROPIC_API_KEY=your_key       # 必需
ANTHROPIC_BASE_URL=https://...   # 可选,用于中转API
CLAUDE_MODEL=claude-3-5-sonnet-20241022  # 可选

# 性能配置
REQUEST_TIMEOUT=300              # 请求超时(秒)
MAX_RETRIES=3                    # 最大重试次数
```

### 作为Python模块使用

你也可以在自己的Python代码中使用DeepRead Pipeline:

#### 1. 使用预定义的Pipeline

```python
from pipeline import create_full_pipeline, create_summary_only_pipeline

# 完整流程: PDF → Gitee → MinerU → 总结
pipeline = create_full_pipeline()
context = {
    "pdf_path": "document.pdf",
    "style": "detailed"  # 可选,默认为detailed
}
result = pipeline.run(context)
print(f"总结已保存到: {result['output_path']}")

# 只生成总结: Markdown → 总结
pipeline = create_summary_only_pipeline()
context = {
    "markdown_path": "document.md",
    "style": "detailed"
}
result = pipeline.run(context)
print(f"总结已保存到: {result['output_path']}")
```

#### 2. 创建自定义Pipeline

```python
from pipeline import (
    Pipeline,
    PDFUploadStep,
    MinerUParseStep,
    SummaryGenerateStep,
    SaveSummaryStep
)

# 创建自定义Pipeline
pipeline = Pipeline("自定义处理流程")
pipeline.add_step(PDFUploadStep())        # 上传PDF到Gitee
pipeline.add_step(MinerUParseStep())      # 使用MinerU解析
pipeline.add_step(SummaryGenerateStep())  # 生成总结
pipeline.add_step(SaveSummaryStep())      # 保存结果

# 运行Pipeline
context = {"pdf_path": "document.pdf", "style": "detailed"}
result = pipeline.run(context)
print(f"处理完成: {result['output_path']}")
```

#### 3. 单独使用某个步骤

```python
from pipeline import PDFUploadStep, MinerUParseStep

# 只上传PDF到Gitee
upload_step = PDFUploadStep()
context = {"pdf_path": "document.pdf"}
result = upload_step.execute(context)
print(f"PDF已上传: {result['gitee_pdf_url']}")

# 只解析PDF(需要提供URL)
parse_step = MinerUParseStep()
context = {"pdf_url": "https://..."}
result = parse_step.execute(context)
print(f"解析完成: {result['markdown_content']}")
```

#### 4. 可用的Pipeline步骤

- `PDFUploadStep`: 上传PDF到Gitee
- `MinerUParseStep`: 使用MinerU解析PDF
- `MarkdownGenerateStep`: 从本地读取Markdown文件
- `SummaryGenerateStep`: 使用Claude生成总结
- `SaveSummaryStep`: 保存总结到文件

## 注意事项

1. **API费用**: 使用MinerU和Claude API都可能产生费用,请注意控制使用量
2. **数据隐私**: 上传到API的PDF内容会被发送到第三方服务器,请注意数据安全
3. **文件大小**: 过大的PDF文件可能导致处理时间较长或超时
4. **语言支持**: 工具支持多种语言,但总结质量可能因语言而异

## 贡献

欢迎提交Issue和Pull Request!

## 许可证

MIT License

## 联系方式

如有问题或建议,请通过GitHub Issues联系。
