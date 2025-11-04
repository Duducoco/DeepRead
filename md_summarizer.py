"""
Markdown总结模块
输入markdown文件，使用大模型进行总结，输出markdown格式的总结
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from llm_client import ClaudeClient, SummaryStyle


class MarkdownSummarizer:
    """Markdown文件总结器"""

    def __init__(self, claude_client: Optional[ClaudeClient] = None):
        """
        初始化Markdown总结器

        Args:
            claude_client: Claude客户端实例，如果不提供则创建新实例
        """
        self.claude_client = claude_client or ClaudeClient()

    def summarize_file(
        self,
        input_md_path: str,
        output_md_path: Optional[str] = None,
        style: SummaryStyle = "detailed",
        custom_prompt: Optional[str] = None,
    ) -> dict:
        """
        总结markdown文件

        Args:
            input_md_path: 输入的markdown文件路径
            output_md_path: 输出的markdown文件路径（可选，默认为输入文件名_summary.md）
            style: 总结风格
            custom_prompt: 自定义总结提示词

        Returns:
            包含处理结果的字典

        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 处理失败
        """
        input_path = Path(input_md_path)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        print(f"\n{'=' * 60}")
        print(f"开始总结Markdown文件: {input_path.name}")
        print(f"{'=' * 60}\n")

        # 步骤1: 读取markdown文件
        print("步骤 1/3: 读取Markdown文件")
        print("-" * 60)
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            print(f"✓ 文件读取成功，长度: {len(markdown_content)} 字符\n")
        except Exception as e:
            print(f"✗ 文件读取失败: {e}")
            raise

        # 步骤2: 使用Claude生成总结
        print("步骤 2/3: 使用Claude生成总结")
        print("-" * 60)
        try:
            summary = self.claude_client.summarize_markdown(
                markdown_content=markdown_content, style=style, custom_prompt=custom_prompt
            )
            print(f"✓ 总结生成成功，长度: {len(summary)} 字符\n")
        except Exception as e:
            print(f"✗ 生成总结失败: {e}")
            raise

        # 步骤3: 保存结果
        print("步骤 3/3: 保存结果")
        print("-" * 60)

        # 确定输出路径
        if output_md_path:
            output_path = Path(output_md_path)
        else:
            output_path = input_path.parent / f"{input_path.stem}_summary.md"

        # 格式化输出内容
        formatted_output = self._format_output(input_path, summary, style)

        # 保存文件
        self._save_file(output_path, formatted_output)
        print(f"✓ 总结已保存到: {output_path}\n")

        # 返回处理结果
        result = {
            "success": True,
            "input_path": str(input_path),
            "output_path": str(output_path),
            "input_length": len(markdown_content),
            "summary_length": len(summary),
            "style": style,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
        }

        print(f"{'=' * 60}")
        print("总结完成!")
        print(f"{'=' * 60}\n")

        return result

    def summarize_text(
        self,
        markdown_content: str,
        style: SummaryStyle = "detailed",
        custom_prompt: Optional[str] = None,
    ) -> str:
        """
        直接总结markdown文本（不读写文件）

        Args:
            markdown_content: markdown内容
            style: 总结风格
            custom_prompt: 自定义总结提示词

        Returns:
            总结文本
        """
        print(f"\n{'=' * 60}")
        print("开始总结Markdown文本")
        print(f"{'=' * 60}\n")

        print(f"文本长度: {len(markdown_content)} 字符")
        print("使用Claude生成总结...\n")

        try:
            summary = self.claude_client.summarize_markdown(
                markdown_content=markdown_content, style=style, custom_prompt=custom_prompt
            )
            print(f"✓ 总结生成成功，长度: {len(summary)} 字符\n")
            return summary
        except Exception as e:
            print(f"✗ 生成总结失败: {e}")
            raise

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

    def _format_output(self, input_path: Path, summary: str, style: str) -> str:
        """
        格式化输出内容

        Args:
            input_path: 输入文件路径
            summary: 总结内容
            style: 总结风格

        Returns:
            格式化后的输出
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        output_lines = [
            "# Markdown文档智能总结",
            "",
            "---",
            "",
            f"**原始文件**: {input_path.name}",
            f"**总结风格**: {style}",
            f"**生成时间**: {timestamp}",
            "**工具**: DeepRead (Claude AI)",
            "",
            "---",
            "",
            "## 总结内容",
            "",
            summary,
            "",
            "---",
            "",
            "*本总结由AI自动生成，仅供参考*",
        ]

        return "\n".join(output_lines)


def main():
    """示例代码"""
    # 创建总结器实例
    summarizer = MarkdownSummarizer()

    # 总结单个markdown文件
    result = summarizer.summarize_file(
        input_md_path="example.md", output_md_path="example_summary.md", style="detailed"
    )

    print(f"总结已保存到: {result['output_path']}")


if __name__ == "__main__":
    main()
