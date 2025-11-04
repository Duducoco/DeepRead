"""
核心业务逻辑模块
整合MinerU和Claude,完成从PDF到总结的完整流程
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from llm_client import ClaudeClient, SummaryStyle
from mineru_client import MinerUClient


class PDFSummarizer:
    """PDF智能总结器"""

    def __init__(
        self,
        mineru_client: Optional[MinerUClient] = None,
        claude_client: Optional[ClaudeClient] = None,
    ):
        """
        初始化PDF总结器

        Args:
            mineru_client: MinerU客户端实例,如果不提供则创建新实例
            claude_client: Claude客户端实例,如果不提供则创建新实例
        """
        self.mineru_client = mineru_client or MinerUClient()
        self.claude_client = claude_client or ClaudeClient()

    def process(
        self,
        pdf_path: str,
        output_path: Optional[str] = None,
        style: SummaryStyle = "detailed",
        custom_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        处理PDF文件:解析为markdown并生成总结

        Args:
            pdf_path: PDF文件路径
            output_path: 输出文件路径(可选)
            style: 总结风格
            custom_prompt: 自定义总结提示词

        Returns:
            包含处理结果的字典

        Raises:
            FileNotFoundError: PDF文件不存在
            ValueError: 处理失败
        """
        pdf_path = Path(pdf_path)
        print(f"\n{'=' * 60}")
        print(f"开始处理PDF: {pdf_path.name}")
        print(f"{'=' * 60}\n")

        # 步骤1: 使用MinerU解析PDF
        print("步骤 1/3: 解析PDF为Markdown")
        print("-" * 60)
        summary_path = None
        try:
            parse_result = self.mineru_client.parse_pdf(str(pdf_path))
            markdown_path = parse_result.get("markdown_path")
            summary_path = Path(markdown_path).parent / "summary.md"

            if not markdown_path:
                raise ValueError("MinerU返回的markdown内容为空")

            with open(markdown_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            print(f"✓ PDF解析成功,markdown长度: {len(markdown_content)} 字符\n")

        except Exception as e:
            print(f"✗ PDF解析失败: {e}")
            raise

        # 步骤2: 使用Claude生成总结
        print("步骤 3/4: 使用Claude生成总结")
        print("-" * 60)
        try:
            summary = self.claude_client.summarize_markdown(
                markdown_content=markdown_content, style=style, custom_prompt=custom_prompt
            )
            print(f"✓ 总结生成成功,长度: {len(summary)} 字符\n")

        except Exception as e:
            print(f"✗ 生成总结失败: {e}")
            raise

        # 步骤3: 保存结果
        print("步骤 4/4: 保存结果")
        print("-" * 60)
        self._save_file(summary_path, summary)
        print(f"✓ 总结已保存到: {summary_path}\n")

        # 返回处理结果
        result = {
            "success": True,
            "pdf_path": str(pdf_path),
            "output_path": str(summary_path),
            "markdown_length": len(markdown_content),
            "summary_length": len(summary),
            "style": style,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
        }

        print(f"{'=' * 60}")
        print("处理完成!")
        print(f"{'=' * 60}\n")

        return result

    def _save_file(self, path: Path, content: str):
        """
        保存文件

        Args:
            path: 文件路径
            content: 文件内容
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def main_example():
    """示例代码"""
    summarizer = PDFSummarizer()

    # 处理单个PDF
    result = summarizer.process(
        pdf_path="example.pdf",
        style="detailed",
    )

    print(f"处理结果: {result['output_path']}")


if __name__ == "__main__":
    main_example()
