"""
Pipeline步骤类
定义各个具体的处理步骤,直接集成API调用逻辑
"""

import base64
import hashlib
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import requests
from anthropic import Anthropic
from tqdm import tqdm

from config import config

from .base import PipelineStep


class PDFUploadStep(PipelineStep):
    """PDF上传步骤 - 上传PDF到Gitee获取URL"""

    def __init__(self):
        """初始化PDF上传步骤"""
        super().__init__("上传PDF到Gitee")

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        上传PDF到Gitee

        需要的context字段:
            - pdf_path: PDF文件路径

        返回的结果:
            - gitee_pdf_url: Gitee PDF文件URL
            - gitee_pdf_raw_url: Gitee PDF原始下载URL
        """
        pdf_path = context.get("pdf_path")
        if not pdf_path:
            raise ValueError("context中缺少pdf_path字段")

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        # 读取文件
        with open(pdf_path, "rb") as f:
            content = f.read()

        # 计算文件的SHA-256哈希值
        file_sha = hashlib.sha256(content).hexdigest()

        # 获取文件扩展名
        file_ext = pdf_path.suffix

        # 使用SHA值作为文件名
        now = datetime.now()
        gitee_path = f"{config.GITEE_UPLOAD_PATH}/{now.year}/{now.month:02d}/{file_sha}{file_ext}"

        print(f"  - 文件SHA: {file_sha}")

        # 先检查文件是否已存在
        check_url = f"https://gitee.com/api/v5/repos/{config.GITEE_OWNER}/{config.GITEE_REPO}/contents/{gitee_path}"
        check_params = {
            "access_token": config.GITEE_ACCESS_TOKEN,
            "ref": config.GITEE_BRANCH,
        }

        try:
            check_response = requests.get(check_url, params=check_params, timeout=config.REQUEST_TIMEOUT)
            if check_response.status_code == 200:
                # 文件已存在,直接返回
                result = check_response.json()

                # Gitee API 可能返回列表或单个对象
                if isinstance(result, list):
                    # 如果是列表,取第一个元素
                    file_info = result[0] if result else None
                else:
                    # 如果是单个对象
                    file_info = result

                if file_info:
                    gitee_pdf_url = file_info["html_url"]
                    gitee_pdf_raw_url = file_info["download_url"]

                    print(f"  ✓ 文件已存在,复用已有文件")
                    print(f"  - PDF URL: {gitee_pdf_url}")
                    print(f"  - Raw URL: {gitee_pdf_raw_url}")

                    return {
                        "gitee_pdf_url": gitee_pdf_url,
                        "gitee_pdf_raw_url": gitee_pdf_raw_url,
                        "original_filename": pdf_path.stem,  # 保存原始文件名(不含扩展名)
                    }
        except (requests.RequestException, KeyError, IndexError):
            # 文件不存在或检查失败,继续上传
            pass

        # Base64编码
        content_b64 = base64.b64encode(content).decode("utf-8")

        # 调用Gitee API上传新文件
        data = {
            "access_token": config.GITEE_ACCESS_TOKEN,
            "content": content_b64,
            "message": f"Upload PDF: {pdf_path.name} (SHA: {file_sha})",
            "branch": config.GITEE_BRANCH,
        }

        response = requests.post(check_url, json=data, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        result = response.json()

        gitee_pdf_url = result["content"]["html_url"]
        gitee_pdf_raw_url = result["content"]["download_url"]

        print(f"  ✓ 文件上传成功")
        print(f"  - PDF URL: {gitee_pdf_url}")
        print(f"  - Raw URL: {gitee_pdf_raw_url}")

        return {
            "gitee_pdf_url": gitee_pdf_url,
            "gitee_pdf_raw_url": gitee_pdf_raw_url,
            "original_filename": pdf_path.stem,  # 保存原始文件名(不含扩展名)
        }


class MinerUParseStep(PipelineStep):
    """MinerU解析步骤 - 使用MinerU解析PDF URL为Markdown"""

    def __init__(self):
        """初始化MinerU解析步骤"""
        super().__init__("MinerU解析PDF")

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用MinerU解析PDF URL

        需要的context字段:
            - gitee_pdf_raw_url: Gitee PDF原始下载URL
            - original_filename: 原始文件名(不含扩展名,可选)

        返回的结果:
            - markdown_path: Markdown文件路径
            - markdown_content: Markdown内容
            - markdown_length: Markdown长度
        """
        pdf_url = context.get("gitee_pdf_raw_url")
        if not pdf_url:
            raise ValueError("context中缺少gitee_pdf_raw_url字段")

        # 优先使用原始文件名,如果没有则从URL提取
        pdf_filename = context.get("original_filename")
        if not pdf_filename:
            pdf_filename = Path(pdf_url).stem

        # 步骤1: 调用MinerU API
        print("  [1/2] 调用MinerU API...")
        task_id = self._call_mineru_api(pdf_url)
        print(f"  ✓ 任务ID: {task_id}")

        # 步骤2: 等待并下载结果
        print("  [2/2] 等待解析完成...")
        result = self._wait_and_download(task_id, pdf_filename)

        # 读取Markdown内容
        markdown_path = result["markdown_path"]
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        print(f"  ✓ Markdown文件: {markdown_path}")
        print(f"  ✓ Markdown长度: {len(markdown_content)} 字符")

        return {
            "markdown_path": str(markdown_path),
            "markdown_content": markdown_content,
            "markdown_length": len(markdown_content),
        }

    def _call_mineru_api(self, pdf_url: str) -> str:
        """调用MinerU API"""
        url = config.MINERU_API_URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.MINERU_API_KEY}",
        }
        data = {"url": pdf_url, "is_ocr": False, "enable_formula": True}

        for attempt in range(config.MAX_RETRIES):
            try:
                response = requests.post(
                    url, json=data, headers=headers, timeout=config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                result = response.json()
                task_id = result.get("data", {}).get("task_id")
                if not task_id:
                    raise ValueError(f"API返回无效响应: {result}")
                return task_id
            except requests.RequestException:
                if attempt == config.MAX_RETRIES - 1:
                    raise
                print(f"  请求失败,重试中... ({attempt + 1}/{config.MAX_RETRIES})")
                time.sleep(2**attempt)

    def _wait_and_download(self, task_id: str, pdf_filename: str) -> Dict[str, Any]:
        """等待任务完成并下载结果"""
        url = f"https://mineru.net/api/v4/extract/task/{task_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.MINERU_API_KEY}",
        }

        start_time = time.time()

        while True:
            if time.time() - start_time > config.REQUEST_TIMEOUT:
                raise TimeoutError(f"等待结果超时(任务ID: {task_id})")

            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 0:
                    raise ValueError(f"API返回错误: {result.get('msg', '未知错误')}")

                data = result.get("data", {})
                state = data.get("state")

                if state == "done":
                    # 下载结果
                    zip_url = data.get("full_zip_url")
                    if not zip_url:
                        raise ValueError("未找到下载链接")

                    # 下载并解压
                    zip_path = self._download_zip(zip_url, task_id)
                    extract_folder = self._extract_zip(zip_path, pdf_filename)

                    # 删除json和pdf文件
                    for item in Path(extract_folder).iterdir():
                        if item.suffix.lower() in [".json", ".pdf"]:
                            item.unlink()

                    return {
                        "task_id": task_id,
                        "markdown_path": Path(extract_folder) / "full.md",
                        "extract_folder": extract_folder,
                    }

                elif state == "failed":
                    raise ValueError(f"任务失败: {data.get('err_msg', '未知错误')}")

                elif state == "running":
                    progress = data.get("extract_progress", {})
                    extracted = progress.get("extracted_pages", 0)
                    total = progress.get("total_pages", 0)
                    if total > 0:
                        print(f"\r  解析中: {extracted}/{total} 页", end="", flush=True)
                    else:
                        print(".", end="", flush=True)

            except requests.RequestException as e:
                print(f"\n  检查状态失败: {e}")

            time.sleep(5)

    def _download_zip(self, zip_url: str, task_id: str) -> Path:
        """下载ZIP文件"""
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        zip_path = output_dir / f"{task_id}.zip"

        response = requests.get(zip_url, stream=True, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return zip_path

    def _extract_zip(self, zip_path: Path, pdf_filename: str) -> str:
        """解压ZIP文件"""
        output_dir = Path("output")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        extract_folder = output_dir / f"{timestamp}_{pdf_filename}"

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)

        # 删除ZIP文件
        zip_path.unlink()

        return str(extract_folder)


class MarkdownGenerateStep(PipelineStep):
    """Markdown生成步骤 - 从本地或远程获取Markdown内容"""

    def __init__(self):
        """初始化Markdown生成步骤"""
        super().__init__("获取Markdown内容")

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        从已有路径或URL获取Markdown内容

        需要的context字段:
            - markdown_path: Markdown文件路径(本地)
            或
            - gitee_raw_url: Gitee原始文件URL(远程)

        返回的结果:
            - markdown_content: Markdown内容
            - markdown_length: Markdown长度
        """
        # 如果已经有markdown_content,直接返回
        if "markdown_content" in context:
            print("  - 使用已有的Markdown内容")
            return {}

        # 优先使用本地文件
        markdown_path = context.get("markdown_path")
        if markdown_path:
            with open(markdown_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            print(f"  - 从本地读取: {markdown_path}")
            print(f"  - Markdown长度: {len(markdown_content)} 字符")

            return {
                "markdown_content": markdown_content,
                "markdown_length": len(markdown_content),
            }

        # 如果有Gitee URL,从远程获取
        gitee_raw_url = context.get("gitee_raw_url")
        if gitee_raw_url:
            response = requests.get(gitee_raw_url)
            response.raise_for_status()
            markdown_content = response.text

            print(f"  - 从Gitee获取: {gitee_raw_url}")
            print(f"  - Markdown长度: {len(markdown_content)} 字符")

            return {
                "markdown_content": markdown_content,
                "markdown_length": len(markdown_content),
            }

        raise ValueError("context中既没有markdown_path也没有gitee_raw_url")


class SummaryGenerateStep(PipelineStep):
    """总结生成步骤 - 使用Claude生成总结"""

    def __init__(self):
        """初始化总结生成步骤"""
        super().__init__("生成总结")

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用Claude生成总结

        需要的context字段:
            - markdown_content: Markdown内容
            - style: 总结风格(可选,默认为'detailed')
            - custom_prompt: 自定义提示词(可选)

        返回的结果:
            - summary: 总结内容
            - summary_length: 总结长度
        """
        markdown_content = context.get("markdown_content")
        if not markdown_content:
            raise ValueError("context中缺少markdown_content字段")

        style = context.get("style", "detailed")
        custom_prompt = context.get("custom_prompt")

        # 构建提示词
        if custom_prompt:
            system_prompt = custom_prompt
        else:
            system_prompt = self._get_style_prompt(style)

        print(f"  - 使用模型: {config.CLAUDE_MODEL}")
        print(f"  - 总结风格: {style}")

        # 初始化Claude客户端
        if config.ANTHROPIC_BASE_URL:
            client = Anthropic(api_key=config.ANTHROPIC_API_KEY, base_url=config.ANTHROPIC_BASE_URL)
        else:
            client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

        # 调用API
        try:
            summary_parts = []

            with client.messages.stream(
                model=config.CLAUDE_MODEL,
                max_tokens=30000,
                system=system_prompt,
                messages=[{"role": "user", "content": markdown_content}],
            ) as stream:
                length = 0
                with tqdm(desc="生成中", unit="字符") as pbar:
                    for text in stream.text_stream:
                        summary_parts.append(text)
                        length = length + len(text)
                        pbar.update(len(text))

                # for text in stream.text_stream:
                #     summary_parts.append(text)
                #     length = length + len(text)
                #     print(f"已生成{length}字符.", end="", flush=True)

            print()  # 换行
            summary = "".join(summary_parts)

            print(f"  - 总结长度: {len(summary)} 字符")

            return {
                "summary": summary,
                "summary_length": len(summary),
            }

        except Exception as e:
            raise ValueError(f"Claude API调用失败: {e}")

    def _get_style_prompt(self, style: str) -> str:
        """获取总结风格对应的提示词"""
        if style == "detailed":
            # 从文件读取detailed风格的提示词
            prompt_file = Path("prompts/detailed.md")
            if prompt_file.exists():
                with open(prompt_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                # 如果文件不存在，使用默认提示词
                print(f"  警告: 未找到 {prompt_file},使用默认提示词")
                return self._get_default_prompt()

        # 其他风格可以在这里添加
        else:
            Warning.add_note(f"不支持的总结风格: {style},使用默认提示词")
        return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """获取默认提示词"""
        return """你是一个专业的文档分析助手。请仔细阅读以下markdown文档,并生成一份详细的总结报告。

要求:
1. 总结应该全面深入,包含文档的所有关键信息
2. 保持逻辑清晰,结构完整
3. 使用markdown格式输出
4. 包含以下部分:
   - 核心要点
   - 详细内容
   - 关键结论
   - 实用建议(如果适用)

请开始分析:"""


class SaveSummaryStep(PipelineStep):
    """保存总结步骤 - 保存总结到文件"""

    def __init__(self):
        """初始化保存总结步骤"""
        super().__init__("保存总结")

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存总结到文件

        需要的context字段:
            - summary: 总结内容
            - output_path: 输出文件路径(可选)
            - markdown_path: Markdown文件路径(用于推断输出路径)

        返回的结果:
            - output_path: 输出文件路径
        """
        summary = context.get("summary")
        if not summary:
            raise ValueError("context中缺少summary字段")

        # 确定输出路径
        output_path = context.get("output_path")
        if not output_path:
            markdown_path = context.get("markdown_path")
            if markdown_path:
                output_path = str(Path(markdown_path).parent / "summary.md")
            else:
                output_path = "output/summary.md"

        output_path = Path(output_path)

        # 保存文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"  - 输出文件: {output_path}")

        return {
            "output_path": str(output_path),
        }
