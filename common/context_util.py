# ============================================================
# common/context_util.py
# 测试上下文管理 —— 用例间传递数据的桥梁
# 例如：注册成功后保存 user_id，登录用例读取后发起登录
# 数据存储在 extract.yaml（每次测试会话开始前自动清空）
# ============================================================

import os
from common.yaml_util import write_yaml, read_yaml

# extract.yaml 路径（项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT_FILE = os.path.join(BASE_DIR, "extract.yaml")


def save_context(key: str, value):
    """
    保存上下文数据
    - key: 数据的标识符（如 "current_user"）
    - value: 要保存的值（通常是字典或字符串）
    """
    write_yaml(key, value, EXTRACT_FILE)


def get_context(key: str, default=None):
    """
    读取上下文数据
    - key 不存在时返回 default
    - 用例间共享数据的核心方法
    """
    data = read_yaml(EXTRACT_FILE)
    return data.get(key, default)


def get_users() -> list:
    """获取已注册的用户列表（从上下文中读取）"""
    return get_context("users", [])


def save_users(users: list):
    """保存用户列表到上下文"""
    save_context("users", users)
