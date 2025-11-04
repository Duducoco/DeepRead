"""
Claude API客户端
使用Anthropic的官方SDK调用Claude进行markdown总结
"""

from typing import Literal, Optional

from anthropic import Anthropic

from config import config

SummaryStyle = Literal["concise", "detailed", "bullet", "academic", "casual"]


class ClaudeClient:
    """Claude API客户端类"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        初始化Claude客户端

        Args:
            api_key: Anthropic API密钥,如果不提供则从配置读取
            model: Claude模型名称,如果不提供则从配置读取
            base_url: API的base URL,用于中转API,如果不提供则从配置读取
        """
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        self.model = model or config.CLAUDE_MODEL
        self.base_url = base_url or config.ANTHROPIC_BASE_URL

        # 根据是否有base_url来初始化客户端
        if self.base_url:
            print(f"使用自定义API地址: {self.base_url}")
            self.client = Anthropic(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = Anthropic(api_key=self.api_key)

    def summarize_markdown(
        self,
        markdown_content: str,
        style: SummaryStyle = "detailed",
        custom_prompt: Optional[str] = None,
        max_tokens: int = 30000,
    ) -> str:
        """
        使用Claude总结markdown内容

        Args:
            markdown_content: 需要总结的markdown文本
            style: 总结风格
            custom_prompt: 自定义提示词(如果提供,将覆盖预设风格)
            max_tokens: 最大生成token数

        Returns:
            总结后的文本

        Raises:
            ValueError: 输入内容为空或API调用失败
        """
        if not markdown_content or not markdown_content.strip():
            raise ValueError("Markdown内容不能为空")

        # 构建提示词
        if custom_prompt:
            system_prompt = custom_prompt
        else:
            system_prompt = self._get_style_prompt(style)

        print(f"正在使用Claude {self.model}生成总结...")
        print(f"总结风格: {style}")

        try:
            # 使用流式API调用Claude
            summary_parts = []
            input_tokens = 0
            output_tokens = 0
            char_count = 0

            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": f"论文内容为:\n\n{markdown_content}"}],
            ) as stream:
                for text in stream.text_stream:
                    summary_parts.append(text)
                    char_count += len(text)
                    # 实时显示字数进度（使用\r实现原地更新）
                    print(f"\r生成进度: {char_count} 字符", end="", flush=True)

                # 获取最终的消息以获取token使用情况
                final_message = stream.get_final_message()
                input_tokens = final_message.usage.input_tokens
                output_tokens = final_message.usage.output_tokens

            summary = "".join(summary_parts)
            print(f"\n总结完成! (使用了 {input_tokens} 输入tokens, {output_tokens} 输出tokens)")

            return summary

        except Exception as e:
            raise ValueError(f"调用Claude API失败: {e}")

    def _get_style_prompt(self, style: SummaryStyle) -> str:
        """
        根据风格获取对应的系统提示词

        Args:
            style: 总结风格

        Returns:
            系统提示词
        """

        if style == "detailed":
            with open("prompts/detailed.md", "r", encoding="utf-8") as f:
                prompt = f.read()
        else:
            raise ValueError(f"不支持的总结风格: {style}")

        return prompt
