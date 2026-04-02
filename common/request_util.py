# ============================================================
# common/request_util.py
# HTTP 请求工具类 —— 封装 requests，统一管理请求头、超时、日志和脱敏
# 所有 API 调用都通过这个类发出，保证日志格式一致、敏感信息不泄露
# ============================================================

import requests
import copy
from typing import Dict, Any, Optional
from common.logger import get_logger


class RequestUtil:
    """HTTP 请求封装，支持 Session 复用、全局 Headers、自动日志和敏感字段脱敏"""

    # 脱敏关键词列表 —— 日志中包含这些词的 header 会被替换为 ******
    SENSITIVE_KEYS = ["authorization", "cookie", "token", "password", "secret"]

    def __init__(self, base_url: str = "", default_headers: Optional[Dict] = None, timeout: int = 10):
        """
        初始化请求工具
        :param base_url: API 根地址，如 http://localhost:8080
        :param default_headers: 全局默认请求头（如 Content-Type）
        :param timeout: 默认超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()          # 复用 TCP 连接，性能更好
        self.timeout = timeout
        self.logger = get_logger("RequestUtil")
        self.default_headers = default_headers or {}

    def update_headers(self, headers: Dict[str, str]):
        """更新全局请求头（典型场景：登录后设置 Authorization）"""
        self.default_headers.update(headers)
        self.logger.info(f"更新请求头: {self._mask(self.default_headers)}")

    def close(self):
        """关闭 Session，释放连接池"""
        self.session.close()

    def _mask(self, data: Dict) -> Dict:
        """
        脱敏处理 —— 把敏感字段的值替换为 ******
        用于日志输出，防止 Token、密码等泄露到日志文件
        """
        safe = copy.copy(data)
        for key in safe:
            for sk in self.SENSITIVE_KEYS:
                if sk in key.lower():
                    safe[key] = "******"
                    break
        return safe

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """
        核心请求方法 —— 所有 get/post/put/delete 最终都走这里
        自动处理：URL 拼接 → Headers 合并 → 超时设置 → 日志记录 → 异常捕获
        """
        # 拼接完整 URL（如果设置了 base_url）
        url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path

        # 合并全局 headers + 本次请求 headers（本次优先）
        headers = self.default_headers.copy()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # 设置默认超时
        kwargs.setdefault("timeout", self.timeout)

        # ---- 打印请求日志 ----
        self.logger.info(f"{'='*40}")
        self.logger.info(f"{method.upper()} {url}")
        if headers:
            self.logger.info(f"Headers: {self._mask(headers)}")
        for key in ("params", "data", "json"):
            if key in kwargs and kwargs[key]:
                self.logger.info(f"{key}: {kwargs[key]}")

        # ---- 发送请求 ----
        try:
            resp = self.session.request(method.upper(), url, headers=headers, **kwargs)
            self.logger.info(f"Status: {resp.status_code} | Time: {resp.elapsed.total_seconds():.3f}s")
            # 尝试打印 JSON 响应，失败则截取前 500 字符文本
            try:
                self.logger.info(f"Body: {resp.json()}")
            except Exception:
                self.logger.info(f"Body(text): {resp.text[:500]}")
            return resp
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            raise
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接失败: {url}")
            raise
        except Exception as e:
            self.logger.error(f"请求异常: {e}")
            raise
        finally:
            self.logger.info(f"{'='*40}\n")

    # ---- 快捷方法，直接用 get/post/put/delete 代替 request("GET", ...) ----

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
