"""
配置管理模块
使用python-dotenv从.env文件加载API配置
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# 加载.env文件
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """配置类,管理所有API密钥和设置"""

    # MinerU配置
    MINERU_API_KEY = os.getenv("MINERU_API_KEY")
    MINERU_API_URL = os.getenv("MINERU_API_URL", "https://mineru.net/api/v4/extract/task")

    # Anthropic Claude配置
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")  # 可选,用于中转API
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # 可选,用于中转API
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

    # Gitee配置
    GITEE_ACCESS_TOKEN = os.getenv("GITEE_ACCESS_TOKEN")
    GITEE_OWNER = os.getenv("GITEE_OWNER")
    GITEE_REPO = os.getenv("GITEE_REPO").lower()
    GITEE_BRANCH = os.getenv("GITEE_BRANCH", "master")
    GITEE_UPLOAD_PATH = os.getenv("GITEE_UPLOAD_PATH", "pdfs/")

    # 请求超时设置(秒)
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))

    # 最大重试次数
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    @classmethod
    def validate(cls):
        """验证必需的配置是否已设置"""
        errors = []

        if not cls.MINERU_API_KEY:
            errors.append("MINERU_API_KEY未设置")

        # 至少需要配置一个LLM API
        if not cls.ANTHROPIC_API_KEY and not cls.OPENAI_API_KEY:
            errors.append("ANTHROPIC_API_KEY 和 OPENAI_API_KEY 至少需要设置一个")

        if not cls.GITEE_ACCESS_TOKEN:
            errors.append("GITEE_ACCESS_TOKEN未设置")

        if not cls.GITEE_OWNER:
            errors.append("GITEE_OWNER未设置")

        if not cls.GITEE_REPO:
            errors.append("GITEE_REPO未设置")

        if errors:
            raise ValueError(
                "配置错误:\n"
                + "\n".join(f"  - {err}" for err in errors)
                + "\n\n请在.env文件中设置这些环境变量。"
                "\n可以参考.env.example文件。"
            )

    @classmethod
    def get_summary(cls):
        """获取配置摘要(隐藏敏感信息)"""
        return {
            "MINERU_API_URL": cls.MINERU_API_URL,
            "MINERU_API_KEY": "***" + cls.MINERU_API_KEY[-4:] if cls.MINERU_API_KEY else "Not Set",
            "ANTHROPIC_API_KEY": "***" + cls.ANTHROPIC_API_KEY[-4:]
            if cls.ANTHROPIC_API_KEY
            else "Not Set",
            "ANTHROPIC_BASE_URL": cls.ANTHROPIC_BASE_URL or "Default (https://api.anthropic.com)",
            "CLAUDE_MODEL": cls.CLAUDE_MODEL,
            "OPENAI_API_KEY": "***" + cls.OPENAI_API_KEY[-4:]
            if cls.OPENAI_API_KEY
            else "Not Set",
            "OPENAI_BASE_URL": cls.OPENAI_BASE_URL or "Default (https://api.openai.com)",
            "OPENAI_MODEL": cls.OPENAI_MODEL,
            "GITEE_ACCESS_TOKEN": "***" + cls.GITEE_ACCESS_TOKEN[-4:]
            if cls.GITEE_ACCESS_TOKEN
            else "Not Set",
            "GITEE_OWNER": cls.GITEE_OWNER or "Not Set",
            "GITEE_REPO": cls.GITEE_REPO or "Not Set",
            "GITEE_BRANCH": cls.GITEE_BRANCH,
            "GITEE_UPLOAD_PATH": cls.GITEE_UPLOAD_PATH,
            "REQUEST_TIMEOUT": cls.REQUEST_TIMEOUT,
            "MAX_RETRIES": cls.MAX_RETRIES,
        }


# 导出配置实例
config = Config()
