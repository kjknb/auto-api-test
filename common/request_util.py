# common/request_util.py
import requests
import copy
from typing import Dict, Any, Optional
from common.logger import get_logger


class RequestUtil:
    """HTTP 请求工具类，封装 requests，支持 Session、日志、脱敏"""

    SENSITIVE_KEYS = ["authorization", "cookie", "token", "password", "secret"]

    def __init__(self, base_url: str = "", default_headers: Optional[Dict] = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        self.logger = get_logger("RequestUtil")
        self.default_headers = default_headers or {}

    def update_headers(self, headers: Dict[str, str]):
        """更新全局请求头"""
        self.default_headers.update(headers)
        self.logger.info(f"更新请求头: {self._mask(self.default_headers)}")

    def close(self):
        """关闭 Session"""
        self.session.close()

    def _mask(self, data: Dict) -> Dict:
        """脱敏处理"""
        safe = copy.copy(data)
        for key in safe:
            for sk in self.SENSITIVE_KEYS:
                if sk in key.lower():
                    safe[key] = "******"
                    break
        return safe

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """核心请求方法"""
        url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path

        # 合并 headers
        headers = self.default_headers.copy()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # 设置超时
        kwargs.setdefault("timeout", self.timeout)

        self.logger.info(f"{'='*40}")
        self.logger.info(f"{method.upper()} {url}")
        if headers:
            self.logger.info(f"Headers: {self._mask(headers)}")
        for key in ("params", "data", "json"):
            if key in kwargs and kwargs[key]:
                self.logger.info(f"{key}: {kwargs[key]}")

        try:
            resp = self.session.request(method.upper(), url, headers=headers, **kwargs)
            self.logger.info(f"Status: {resp.status_code} | Time: {resp.elapsed.total_seconds():.3f}s")
            try:
                self.logger.info(f"Body: {resp.json()}")
            except Exception:
                body = resp.text[:500]
                self.logger.info(f"Body(text): {body}")
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

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
