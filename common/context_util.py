# common/context_util.py
import os
from common.yaml_util import write_yaml, read_yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT_FILE = os.path.join(BASE_DIR, "extract.yaml")


def save_context(key: str, value):
    """保存上下文数据到 extract.yaml"""
    write_yaml(key, value, EXTRACT_FILE)


def get_context(key: str, default=None):
    """从 extract.yaml 读取上下文数据"""
    data = read_yaml(EXTRACT_FILE)
    return data.get(key, default)


def get_users():
    """获取 extract.yaml 中保存的用户列表"""
    return get_context("users", [])


def save_users(users: list):
    """保存用户列表到 extract.yaml"""
    save_context("users", users)
