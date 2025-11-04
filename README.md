# DeepRead - PDF智能总结工具

一个强大的PDF智能分析工具,使用Gitee存储PDF,MinerU的API解析PDF为markdown,然后调用Claude大模型生成高质量的文档总结。

## 功能特点

- **Gitee云存储**: 自动将PDF上传到Gitee仓库,永久保存并可分享
- **高精度PDF解析**: 使用MinerU云服务解析PDF,支持复杂文档结构，自动下载并解压解析结果
- **智能AI总结**: 集成Anthropic Claude,提供多种总结风格
- **灵活配置**: 使用dotenv管理API密钥,安全便捷
- **命令行友好**: 简洁的CLI界面,易于使用和自动化
- **Markdown总结**: 支持直接对markdown文件进行智能总结

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
git clone <repository-url>
cd DeepRead
```

### 2. 使用uv创建虚拟环境并安装依赖

```bash
# 创建虚拟环境并安装依赖(一步完成)
uv sync

# 或者分步操作:
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 安装依赖
uv pip install -e .
```

### 3. 配置API密钥

复制`.env.example`为`.env`:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

然后编辑`.env`文件,填入你的API密钥:

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
2. 仓库需要设置为**公开**或确保MinerU能访问
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

### 指定输出文件

```bash
uv run python main.py --input document.pdf --output summary.md
```

### 选择总结风格

```bash
uv run python main.py --input document.pdf --style concise
```

支持的总结风格:
<!-- - `concise` - 简洁模式: 3-5段简要总结 -->
- `detailed` - 详细模式: 全面深入的分析(默认)
<!-- - `bullet` - 要点模式: 分层级的要点列表 -->
<!-- - `academic` - 学术模式: 符合学术规范的总结 -->
<!-- - `casual` - 轻松模式: 易懂的日常语言 -->

### 保存原始Markdown

MinerU解析的原始markdown文件会自动保存在解压后的文件夹中（`output/时间戳_文件名/full.md`）。

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
├── gitee_client.py        # Gitee API客户端
├── mineru_client.py       # MinerU API客户端
├── llm_client.py          # Claude API客户端
├── summarizer.py          # PDF处理核心逻辑
├── md_summarizer.py       # Markdown总结模块
├── main.py                # 命令行入口
└── output/                # 默认输出目录
    └── 时间戳_文件名/     # 解压后的文件夹
        ├── full.md        # 解析的完整markdown
        └── ...            # 其他解析结果文件
```

## 工作流程

DeepRead的处理流程:

1. **上传PDF到Gitee**: 将本地PDF文件上传到Gitee仓库,获取可访问的URL
2. **MinerU解析**: 使用Gitee的raw URL调用MinerU API解析PDF为markdown
3. **下载解析结果**: 自动下载解析结果的ZIP包并解压到 `output/时间戳_文件名/` 目录
4. **Claude总结**: 将markdown内容传递给Claude生成智能总结
5. **保存结果**: 保存总结文件到 `output/文件名_summary.md`

## 输出文件

处理完成后，会生成以下文件：

### 1. 解析结果目录
`output/时间戳_PDF文件名/`
- `full.md` - MinerU解析的完整markdown文件
- 其他解析相关文件（图片、表格等）

### 2. 总结文件
`output/PDF文件名_summary.md` - AI生成的智能总结

总结文件包含：
- 文档元信息（原文件名、生成时间等）
- AI生成的总结内容
- 格式化的markdown排版

## 使用示例

### 示例1: 快速总结学术论文

```bash
uv run python main.py --input research_paper.pdf --style detailed
```

### 示例2: 总结单个PDF并自定义输出路径

```bash
uv run python main.py --input document.pdf --output my_summary.md
```

### 示例3: 使用自定义提示词

```bash
uv run python main.py --input article.pdf --prompt "请用5个要点总结这个文档的关键内容"
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
PDF文件默认按日期组织: `pdfs/2024/01/filename_timestamp.pdf`

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
4. 检查文件是否已存在(文件名冲突)

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

你也可以在自己的Python代码中使用DeepRead:

```python
from summarizer import PDFSummarizer
from md_summarizer import MarkdownSummarizer

# 处理PDF文件
pdf_summarizer = PDFSummarizer()
result = pdf_summarizer.process(
    pdf_path='document.pdf',
    style='detailed'
)
print(f"总结已保存到: {result['output_path']}")

# 处理Markdown文件
md_summarizer = MarkdownSummarizer()
result = md_summarizer.summarize_file(
    input_md_path='document.md',
    style='detailed'
)
print(f"总结已保存到: {result['output_path']}")
```

### 使用uv的优势

**为什么使用uv?**

- **极快的速度**: 比pip快10-100倍
- **可靠的依赖解析**: 自动生成lockfile确保环境一致性
- **简单的命令**: `uv sync`一步完成环境创建和依赖安装
- **无需激活**: `uv run`可直接运行,无需手动激活虚拟环境
- **更好的缓存**: 智能缓存机制减少重复下载

**常用uv命令:**

```bash
# 安装新依赖
uv add package-name

# 安装开发依赖
uv add --dev pytest

# 更新依赖
uv sync --upgrade

# 运行脚本(无需激活环境)
uv run python main.py

# 运行任意命令
uv run pytest
```

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

---

**享受智能文档总结的便利!** 🚀
