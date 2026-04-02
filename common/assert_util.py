# ============================================================
# common/assert_util.py
# 断言工具类 —— 封装 API 测试中常用的断言方法
# 所有断言失败时会自动打印实际值 vs 期望值，方便排查
# ============================================================

import json
from typing import Any
from common.logger import get_logger


class AssertUtil:
    """API 响应断言工具，支持状态码、业务码、JSON 字段、文本包含等断言"""

    logger = get_logger("AssertUtil")

    @staticmethod
    def _get_body(response) -> dict:
        """
        安全地从响应中提取 JSON
        - 先尝试 response.json()
        - 失败再尝试 json.loads(response.text)
        - 都失败返回空字典
        """
        try:
            return response.json()
        except ValueError:
            try:
                return json.loads(response.text)
            except Exception:
                return {}

    @classmethod
    def assert_status_code(cls, response, expected: int):
        """断言 HTTP 状态码（如 200、404、500）"""
        actual = response.status_code
        cls.logger.info(f"断言状态码 >> 实际: {actual}, 期望: {expected}")
        assert actual == expected, f"状态码不匹配: 实际 {actual}, 期望 {expected}"

    @classmethod
    def assert_code(cls, response, expected: Any, key: str = "code"):
        """
        断言业务状态码（JSON 响应中的 code 字段）
        - 不同项目业务码定义不同，key 可自定义
        - 通常 0 表示成功，其他值表示各种错误
        """
        body = cls._get_body(response)
        actual = body.get(key)
        cls.logger.info(f"断言业务码({key}) >> 实际: {actual}, 期望: {expected}")
        assert actual == expected, f"业务码不匹配: 实际 {actual}, 期望 {expected}"

    @classmethod
    def assert_json_path(cls, response, path: str, expected: Any):
        """
        断言 JSON 嵌套字段，支持点号路径
        - 例: assert_json_path(resp, "data.user.name", "张三")
        - 找不到路径时值为 None，断言失败
        """
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
        """断言响应文本中包含指定字符串"""
        actual = response.text
        cls.logger.info(f"断言包含 >> 期望: {text}")
        assert text in actual, f"响应不包含: {text}"

    @classmethod
    def assert_not_empty(cls, response, key: str = None):
        """
        断言响应不为空
        - 指定 key 时：断言 body[key] 存在且非空
        - 不指定 key 时：断言整个响应体非空
        """
        body = cls._get_body(response)
        if key:
            val = body.get(key)
            assert val, f"字段 {key} 为空"
        else:
            assert body, "响应体为空"
        cls.logger.info(f"断言非空 >> {'字段 ' + key if key else '响应体'} 验证通过")

    @classmethod
    def assert_json_path_not_empty(cls, response, path: str):
        """
        断言 JSON 嵌套字段存在且非空（比 assert_json_path 更宽松）
        - 例: assert_json_path_not_empty(resp, "data.token")
        - 只检查字段存在且有值，不检查具体值
        """
        body = cls._get_body(response)
        current = body
        for part in path.split("."):
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = None
                break
        cls.logger.info(f"断言非空字段({path}) >> 值: {current}")
        assert current, f"字段 {path} 为空或不存在"
