"""
Gitee API客户端
用于将PDF文件上传到Gitee仓库并获取可访问的URL
"""

import base64
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from config import config


class GiteeClient:
    """Gitee API客户端类"""

    def __init__(
        self,
        access_token: Optional[str] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        branch: Optional[str] = None,
    ):
        """
        初始化Gitee客户端

        Args:
            access_token: Gitee访问令牌,如果不提供则从配置读取
            owner: 仓库所有者用户名,如果不提供则从配置读取
            repo: 仓库名称,如果不提供则从配置读取
            branch: 分支名称,如果不提供则从配置读取
        """
        self.access_token = access_token or config.GITEE_ACCESS_TOKEN
        self.owner = owner or config.GITEE_OWNER
        if repo:
            self.repo = repo.lower()
        else:
            self.repo = config.GITEE_REPO.lower()
        self.branch = branch or config.GITEE_BRANCH
        self.upload_path = config.GITEE_UPLOAD_PATH
        self.session = requests.Session()

    def upload_pdf(self, pdf_path: str, organize_by_date: bool = True) -> Dict[str, Any]:
        """
        上传PDF文件到Gitee仓库

        Args:
            pdf_path: 本地PDF文件路径
            organize_by_date: 是否按日期组织目录结构

        Returns:
            包含upload_url, download_url等信息的字典

        Raises:
            FileNotFoundError: PDF文件不存在
            requests.RequestException: API请求失败
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        print(f"正在准备上传PDF到Gitee: {pdf_path.name}")

        # 读取文件内容
        with open(pdf_path, "rb") as f:
            file_content = f.read()

        # 生成Gitee中的文件路径
        gitee_file_path = self._generate_file_path(pdf_path.name, organize_by_date)

        # 生成提交信息
        commit_message = f"Upload PDF: {pdf_path.name}"

        # 上传到Gitee
        response = self._upload_to_gitee(
            file_path=gitee_file_path, content=file_content, message=commit_message
        )

        # 提取关键信息
        result = self._parse_response(response, gitee_file_path)

        print("✓ PDF已上传到Gitee")
        print(f"  文件路径: {gitee_file_path}")
        print(f"  下载链接: {result['download_url']}")

        return result

    def _generate_file_path(self, filename: str, organize_by_date: bool) -> str:
        """
        生成Gitee中的文件路径

        Args:
            filename: 原始文件名
            organize_by_date: 是否按日期组织

        Returns:
            Gitee中的完整文件路径
        """
        # 添加时间戳避免文件名冲突
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_without_ext = Path(filename).stem
        ext = Path(filename).suffix
        unique_filename = f"{name_without_ext}_{timestamp}{ext}"

        # 构建路径
        if organize_by_date:
            date_path = datetime.now().strftime("%Y/%m")
            full_path = f"{self.upload_path}{date_path}/{unique_filename}"
        else:
            full_path = f"{self.upload_path}{unique_filename}"

        # 移除开头的斜杠(如果有)
        return full_path.lstrip("/")

    def _upload_to_gitee(self, file_path: str, content: bytes, message: str) -> Dict[str, Any]:
        """
        调用Gitee API上传文件

        Args:
            file_path: Gitee中的文件路径
            content: 文件内容(字节)
            message: 提交信息

        Returns:
            Gitee API响应

        Raises:
            requests.RequestException: API请求失败
        """
        url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/contents/{file_path}"

        # Base64编码文件内容
        content_base64 = base64.b64encode(content).decode("utf-8")

        data = {
            "access_token": self.access_token,
            "content": content_base64,
            "message": message,
            "branch": self.branch,
        }

        # 重试机制
        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.post(url, json=data, timeout=config.REQUEST_TIMEOUT)
                print(response)
                # 检查响应状态
                if response.status_code == 201:
                    return response.json()
                elif response.status_code == 400:
                    error_data = response.json()
                    if (
                        "message" in error_data
                        and "already exists" in error_data["message"].lower()
                    ):
                        # 文件已存在,尝试使用新文件名
                        raise ValueError(f"文件已存在于Gitee: {file_path}")
                    else:
                        raise ValueError(f"Gitee API错误: {error_data}")
                else:
                    response.raise_for_status()

            except requests.RequestException:
                if attempt == config.MAX_RETRIES - 1:
                    raise
                print(f"上传失败,重试中... ({attempt + 1}/{config.MAX_RETRIES})")
                time.sleep(2**attempt)  # 指数退避

        raise RuntimeError("上传失败,已达到最大重试次数")

    def _parse_response(self, response: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """
        解析Gitee API响应,提取关键信息

        Args:
            response: Gitee API响应
            file_path: 文件路径

        Returns:
            包含关键信息的字典
        """
        content_data = response.get("content", {})

        # 提取download_url (raw URL)
        download_url = content_data.get("download_url", "")

        # 如果download_url不存在,手动构建
        if not download_url:
            download_url = (
                f"https://gitee.com/{self.owner}/{self.repo}/raw/{self.branch}/{file_path}"
            )

        return {
            "success": True,
            "file_path": file_path,
            "download_url": download_url,  # 这是MinerU需要的raw URL
        }
