"""
MinerU API客户端
用于将PDF文件通过Gitee URL传递给MinerU并获取markdown结果
"""

import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from config import config
from gitee_client import GiteeClient


class MinerUClient:
    """MinerU API客户端类"""

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        初始化MinerU客户端

        Args:
            api_key: MinerU API密钥,如果不提供则从配置读取
            api_url: MinerU API地址,如果不提供则从配置读取
        """
        self.api_key = api_key or config.MINERU_API_KEY
        self.api_url = api_url or config.MINERU_API_URL
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        )
        self.gitee_client = GiteeClient()

    def parse_pdf(self, pdf_path: str, wait_for_result: bool = True) -> Dict[str, Any]:
        """
        解析PDF文件为markdown
        流程: 本地PDF -> 上传到Gitee -> 获取URL -> MinerU解析URL

        Args:
            pdf_path: PDF文件路径
            wait_for_result: 是否等待解析完成

        Returns:
            包含markdown内容和Gitee信息的字典

        Raises:
            FileNotFoundError: PDF文件不存在
            requests.RequestException: API请求失败
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        print("\n步骤 1: 上传PDF到Gitee")
        print("-" * 60)

        # 上传PDF到Gitee
        try:
            gitee_result = self.gitee_client.upload_pdf(str(pdf_path))
            pdf_url = gitee_result["download_url"]
        except Exception as e:
            raise ValueError(f"上传PDF到Gitee失败: {e}")

        print("\n步骤 2: 使用MinerU解析PDF")
        print("-" * 60)
        print(f"PDF URL: {pdf_url}")

        # 使用URL调用MinerU API
        response = self._parse_from_url(pdf_url)
        task_id = response.get("data").get("task_id")
        if not task_id:
            raise ValueError(f"API返回无效响应: {response}")

        print(f"解析任务已创建,任务ID: {task_id}")

        if wait_for_result:
            # 传递PDF文件名（不含扩展名）
            pdf_filename = pdf_path.stem
            result = self._wait_for_result(task_id, pdf_filename=pdf_filename)
            # 添加Gitee信息到结果中
            result["gitee_info"] = gitee_result
            return result
        else:
            return {"task_id": task_id, "status": "processing", "gitee_info": gitee_result}

    def _parse_from_url(self, pdf_url: str) -> Dict[str, Any]:
        """
        使用PDF URL调用MinerU API解析

        Args:
            pdf_url: PDF文件的URL(Gitee raw URL)

        Returns:
            API响应数据

        Raises:
            requests.RequestException: 请求失败
        """
        parse_url = f"{self.api_url}"

        data = {"url": pdf_url, "is_ocr": False, "enable_formula": True}

        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.post(parse_url, json=data, timeout=config.REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.RequestException:
                if attempt == config.MAX_RETRIES - 1:
                    raise
                print(f"请求失败,重试中... ({attempt + 1}/{config.MAX_RETRIES})")
                time.sleep(2**attempt)  # 指数退避

    def _wait_for_result(
        self,
        task_id: str,
        pdf_filename: str = None,
        check_interval: int = 5,
        output_dir: str = "output",
    ) -> Dict[str, Any]:
        """
        等待任务完成并获取结果

        Args:
            task_id: 任务ID
            pdf_filename: PDF文件名（不含扩展名），用于命名解压后的文件夹
            check_interval: 检查间隔(秒)
            output_dir: 输出目录，用于保存下载的文件

        Returns:
            包含markdown内容的结果

        Raises:
            TimeoutError: 等待超时
            ValueError: 任务失败
        """
        # 修复URL格式：https://mineru.net/api/v4/extract/task/{task_id}
        result_url = f"https://mineru.net/api/v4/extract/task/{task_id}"
        start_time = time.time()

        print("正在处理PDF,请稍候...")

        while True:
            if time.time() - start_time > config.REQUEST_TIMEOUT:
                raise TimeoutError(f"等待结果超时(任务ID: {task_id})")

            try:
                response = self.session.get(result_url, timeout=30)
                response.raise_for_status()
                result = response.json()

                # 根据API文档，响应格式为 {"code": 0, "msg": "ok", "data": {...}}
                code = result.get("code")
                if code != 0:
                    msg = result.get("msg", "未知错误")
                    raise ValueError(f"API返回错误: {msg}")

                data = result.get("data", {})
                state = data.get("state")

                # 当state为"done"时表示任务完成
                if state == "done":
                    print("\nPDF解析完成!")

                    # 获取 full_zip_url 并下载
                    full_zip_url = data.get("full_zip_url")
                    if full_zip_url:
                        print(f"正在下载结果文件: {full_zip_url}")
                        zip_path = self._download_zip(full_zip_url, task_id, output_dir)

                        # 解压缩文件
                        extract_folder = self._extract_zip(zip_path, pdf_filename, output_dir)
                        # 删除extract_folder中的json文件和pdf文件
                        for item in Path(extract_folder).iterdir():
                            if item.suffix.lower() in [".json", ".pdf"]:
                                item.unlink()

                        return {
                            "task_id": data.get("task_id", task_id),
                            "state": "done",
                            "full_zip_url": full_zip_url,
                            "zip_path": zip_path,
                            "extract_folder": extract_folder,
                            "markdown_path": Path(extract_folder) / "full.md",
                        }
                    else:
                        print("警告: 未找到 full_zip_url")
                        return {"task_id": data.get("task_id", task_id), "state": "done"}
                elif state == "failed":
                    error_msg = data.get("err_msg", "未知错误")
                    raise ValueError(f"任务失败: {error_msg}")
                elif state == "pending":
                    print("排队中...", end="", flush=True)
                elif state == "running":
                    # 显示解析进度
                    progress = data.get("extract_progress", {})
                    extracted_pages = progress.get("extracted_pages", 0)
                    total_pages = progress.get("total_pages", 0)
                    if total_pages > 0:
                        print(f"\r正在解析: {extracted_pages}/{total_pages} 页", end="", flush=True)
                    else:
                        print(".", end="", flush=True)
                elif state == "converting":
                    print("正在转换格式...", end="", flush=True)
                else:
                    print(f"状态: {state}", end="", flush=True)

            except requests.RequestException as e:
                print(f"\n检查状态失败: {e}")

            time.sleep(check_interval)

    def _download_zip(self, zip_url: str, task_id: str, output_dir: str = "output") -> str:
        """
        下载解析结果的ZIP文件

        Args:
            zip_url: ZIP文件的URL
            task_id: 任务ID，用于命名文件
            output_dir: 输出目录

        Returns:
            下载的ZIP文件路径

        Raises:
            requests.RequestException: 下载失败
        """
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        zip_filename = f"{task_id}.zip"
        zip_filepath = output_path / zip_filename

        # 下载文件
        try:
            response = requests.get(zip_url, stream=True, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()

            # 获取文件大小
            total_size = int(response.headers.get("content-length", 0))

            # 写入文件并显示进度
            with open(zip_filepath, "wb") as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    chunk_size = 8192
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end="", flush=True)
                    print()  # 换行

            print(f"文件已保存到: {zip_filepath}")
            return str(zip_filepath)

        except Exception as e:
            if zip_filepath.exists():
                zip_filepath.unlink()  # 删除不完整的文件
            raise ValueError(f"下载ZIP文件失败: {e}")

    def _extract_zip(
        self, zip_path: str, pdf_filename: str = None, output_dir: str = "output"
    ) -> str:
        """
        解压ZIP文件到指定目录

        Args:
            zip_path: ZIP文件路径
            pdf_filename: PDF文件名（不含扩展名），用于命名文件夹
            output_dir: 输出目录

        Returns:
            解压后的文件夹路径

        Raises:
            zipfile.BadZipFile: ZIP文件损坏
        """
        zip_path = Path(zip_path)
        output_path = Path(output_dir)

        # 生成文件夹名：时间戳+PDF文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if pdf_filename:
            folder_name = f"{timestamp}_{pdf_filename}"
        else:
            folder_name = f"{timestamp}_{zip_path.stem}"

        extract_folder = output_path / folder_name

        try:
            print(f"\n正在解压文件到: {extract_folder}")

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_folder)

            print(f"解压完成! 文件位于: {extract_folder}")

            # 删除ZIP文件
            zip_path.unlink()
            print(f"已删除临时ZIP文件: {zip_path}")

            return str(extract_folder)

        except zipfile.BadZipFile as e:
            raise ValueError(f"ZIP文件损坏: {e}")
        except Exception as e:
            raise ValueError(f"解压文件失败: {e}")
