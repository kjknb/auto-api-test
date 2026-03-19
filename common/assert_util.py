# common/assert_util.py
import json
from typing import Any
from common.logger import get_logger


class AssertUtil:
    """断言工具类，封装常用断言方法"""

    logger = get_logger("AssertUtil")

    @staticmethod
    def _get_body(response) -> dict:
        """安全获取 JSON 响应体"""
        try:
            return response.json()
        except ValueError:
            try:
                return json.loads(response.text)
            except Exception:
                return {}

    @classmethod
    def assert_status_code(cls, response, expected: int):
        """断言 HTTP 状态码"""
        actual = response.status_code
        cls.logger.info(f"断言状态码 >> 实际: {actual}, 期望: {expected}")
        assert actual == expected, f"状态码不匹配: 实际 {actual}, 期望 {expected}"

    @classmethod
    def assert_code(cls, response, expected: Any, key: str = "code"):
        """断言业务状态码"""
        body = cls._get_body(response)
        actual = body.get(key)
        cls.logger.info(f"断言业务码({key}) >> 实际: {actual}, 期望: {expected}")
        assert actual == expected, f"业务码不匹配: 实际 {actual}, 期望 {expected}"

    @classmethod
    def assert_json_path(cls, response, path: str, expected: Any):
        """断言 JSON 嵌套字段，支持点号路径如 data.user.name"""
        body = cls._get_body(response)
        current = body
        for part in path.split("."):
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = None
                break
        cls.logger.info(f"断言字段({path}) >> 实际: {current}, 期望: {expected}")
        assert current == expected, f"字段 {path} 不匹配: 实际 {current}, 期望 {expected}"

    @classmethod
    def assert_contains(cls, response, text: str):
        """断言响应文本包含指定内容"""
        actual = response.text
        cls.logger.info(f"断言包含 >> 期望: {text}")
        assert text in actual, f"响应不包含: {text}"

    @classmethod
    def assert_not_empty(cls, response, key: str = None):
        """断言响应不为空，可指定 key"""
        body = cls._get_body(response)
        if key:
            val = body.get(key)
            assert val, f"字段 {key} 为空"
        else:
            assert body, "响应体为空"
        cls.logger.info(f"断言非空 >> {'字段 ' + key if key else '响应体'} 验证通过")
