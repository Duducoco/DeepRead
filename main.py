#!/usr/bin/env python3
"""
DeepRead - PDF智能总结工具
使用MinerU解析PDF,然后用Claude生成总结
"""

import argparse
import sys
from pathlib import Path

from config import Config


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="DeepRead - PDF智能总结工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个PDF文件(完整流程)
  python main.py --input document.pdf

  # 单步操作 - 解析PDF(自动上传Gitee,解析,下载结果)
  python main.py --step parse --input document.pdf

  # 单步操作 - 从Markdown生成总结
  python main.py --step summarize --input output/document/document.md

  # 指定总结风格
  python main.py --input document.pdf --style detailed

  # 使用自定义提示词
  python main.py --input document.pdf --prompt "请用5个要点总结这个文档"

总结风格说明:
  detailed - 详细模式: 全面深入的分析(默认)

单步模式说明:
  parse     - 解析PDF为Markdown(包含上传到Gitee)
  summarize - 只从Markdown生成总结
        """,
    )

    parser.add_argument(
        "-i", "--input", required=True, metavar="FILE", help="输入文件路径(PDF或Markdown)"
    )

    parser.add_argument(
        "-s", "--style", choices=["detailed"], default="detailed", help="总结风格(默认: detailed)"
    )

    parser.add_argument("-p", "--prompt", metavar="TEXT", help="自定义总结提示词(将覆盖预设风格)")

    parser.add_argument("--step", choices=["parse", "summarize"], help="单步执行模式")

    parser.add_argument("--config", action="store_true", help="显示当前配置信息")

    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细日志")

    return parser.parse_args()


def validate_input(input_path: str, expected_extension: str = None) -> Path:
    """
    验证输入文件

    Args:
        input_path: 输入文件路径
        expected_extension: 期望的文件扩展名(如'.pdf', '.md'),None表示不限制

    Returns:
        验证后的Path对象

    Raises:
        SystemExit: 如果文件不存在或扩展名不匹配
    """
    path = Path(input_path)

    if not path.exists():
        print(f"文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not path.is_file():
        print(f"不是文件: {input_path}", file=sys.stderr)
        sys.exit(1)

    if expected_extension and path.suffix.lower() != expected_extension:
        print(f"文件类型错误,期望{expected_extension}文件: {input_path}", file=sys.stderr)
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

    # 根据不同模式处理
    try:
        if args.step:
            # 单步模式
            return handle_step_mode(args)
        else:
            # 完整流程模式
            return handle_full_mode(args)

    except KeyboardInterrupt:
        print("\n\n用户中断", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n处理过程中发生错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def handle_step_mode(args) -> int:
    """
    处理单步模式

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from pipeline import (
        MinerUParseStep,
        PDFUploadStep,
        Pipeline,
        SaveSummaryStep,
        SummaryGenerateStep,
    )

    if args.step == "parse":
        # 解析PDF(上传Gitee + 调用MinerU + 下载结果)
        input_path = validate_input(args.input, ".pdf")

        pipeline = Pipeline("PDF解析")
        pipeline.add_step(PDFUploadStep())  # 上传PDF
        pipeline.add_step(MinerUParseStep())  # 解析URL

        context = {"pdf_path": str(input_path)}
        result = pipeline.run(context)

        print("\n✓ 解析完成!")
        print(f"  Markdown文件: {result['markdown_path']}")
        return 0

    elif args.step == "summarize":
        # 从Markdown生成总结
        input_path = validate_input(args.input, ".md")

        pipeline = Pipeline("生成总结")
        pipeline.add_step(SummaryGenerateStep())
        pipeline.add_step(SaveSummaryStep())

        context = {
            "markdown_path": str(input_path),
            "style": args.style,
            "custom_prompt": args.prompt,
        }
        result = pipeline.run(context)

        print("\n✓ 总结完成!")
        print(f"  输出文件: {result['output_path']}")
        return 0

    return 1


def handle_full_mode(args) -> int:
    """
    处理完整流程模式

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    from pipeline import create_full_pipeline, create_summary_only_pipeline

    # 验证输入文件(PDF或Markdown)
    input_path = validate_input(args.input)

    # 根据文件类型选择处理方式
    if input_path.suffix.lower() == ".pdf":
        # PDF完整流程
        pipeline = create_full_pipeline()
        context = {
            "pdf_path": str(input_path),
            "style": args.style,
            "custom_prompt": args.prompt,
        }
    elif input_path.suffix.lower() == ".md":
        # Markdown总结流程
        pipeline = create_summary_only_pipeline()
        context = {
            "markdown_path": str(input_path),
            "style": args.style,
            "custom_prompt": args.prompt,
        }
    else:
        print(f"不支持的文件类型: {input_path.suffix}", file=sys.stderr)
        return 1

    # 运行Pipeline
    try:
        result = pipeline.run(context)
        print("\n✓ 处理成功!")
        print(f"  输出文件: {result['output_path']}")
        return 0
    except Exception as e:
        print(f"\n✗ 处理失败: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
