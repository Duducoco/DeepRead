#!/usr/bin/env python3
"""
DeepRead - PDF智能总结工具
使用MinerU解析PDF,然后用Claude生成总结
"""

import argparse
import sys
from pathlib import Path

from config import Config
from summarizer import PDFSummarizer


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="DeepRead - PDF智能总结工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个PDF文件
  python main.py --input document.pdf

  # 指定输出文件和总结风格
  python main.py --input document.pdf --output summary.md --style detailed

  # 使用自定义提示词
  python main.py --input document.pdf --prompt "请用5个要点总结这个文档"

总结风格说明:
  detailed - 详细模式: 全面深入的分析(默认)
        """,
    )

    parser.add_argument("-i", "--input", required=True, metavar="FILE", help="PDF文件路径")

    parser.add_argument("-o", "--output", metavar="FILE", help="输出文件路径")

    parser.add_argument(
        "-s", "--style", choices=["detailed"], default="detailed", help="总结风格(默认: detailed)"
    )

    parser.add_argument("-p", "--prompt", metavar="TEXT", help="自定义总结提示词(将覆盖预设风格)")

    parser.add_argument("--config", action="store_true", help="显示当前配置信息")

    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细日志")

    return parser.parse_args()


def validate_input(pdf_path: str) -> Path:
    """
    验证输入文件

    Args:
        pdf_path: PDF文件路径

    Returns:
        验证后的Path对象

    Raises:
        SystemExit: 如果文件不存在或不是PDF
    """
    path = Path(pdf_path)

    if not path.exists():
        print(f"文件不存在: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if not path.is_file():
        print(f"不是文件: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if path.suffix.lower() != ".pdf":
        print(f"不是PDF文件: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    return path


def show_config():
    """显示配置信息"""
    print("\n当前配置:")
    print("=" * 60)
    config_summary = Config.get_summary()
    for key, value in config_summary.items():
        print(f"  {key:20s}: {value}")
    print("=" * 60)
    print()


def main():
    """主函数"""
    args = parse_args()

    # 显示配置
    if args.config:
        show_config()
        return 0

    # 验证配置
    try:
        Config.validate()
    except ValueError as e:
        print(f"配置错误: {e}", file=sys.stderr)
        print("\n请检查.env文件是否正确配置。", file=sys.stderr)
        print("你可以复制.env.example为.env并填入你的API密钥。", file=sys.stderr)
        return 1

    # 验证输入文件
    pdf_path = validate_input(args.input)

    # 创建总结器
    try:
        summarizer = PDFSummarizer()
    except Exception as e:
        print(f"初始化失败: {e}", file=sys.stderr)
        return 1

    # 处理文件
    try:
        result = summarizer.process(
            pdf_path=str(pdf_path),
            output_path=args.output,
            style=args.style,
            custom_prompt=args.prompt,
        )

        if result["success"]:
            print("\n✓ 处理成功!")
            print(f"  输出文件: {result['output_path']}")
            return 0
        else:
            print("\n✗ 处理失败", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\n\n用户中断", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n处理过程中发生错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
