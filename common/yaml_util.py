# ============================================================
# common/yaml_util.py
# YAML 文件读写工具 —— 配置加载、测试数据读取、上下文传递的基础
# 所有 YAML 操作都走这里，统一管理文件读写
# ============================================================

import os
import yaml

# extract.yaml 默认路径（用例间传递数据用）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT_PATH = os.path.join(BASE_DIR, "extract.yaml")


def read_yaml(file_path: str) -> dict:
    """
    读取 YAML 文件，返回字典
    - 文件不存在时返回空字典（不会报错）
    - 支持中文等 Unicode 字符
    """
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(key, value, file_path=EXTRACT_PATH):
    """
    写入指定 key-value 到 YAML 文件
    - 文件中原有其他 key 会保留
    - 文件不存在会自动创建
    """
    data = read_yaml(file_path)
    data[key] = value
    _save_yaml(file_path, data)


def append_yaml(key, value, file_path=EXTRACT_PATH):
    """
    追加值到 YAML 中的列表 key
    - key 不存在时自动创建空列表
    - key 已存在但不是列表时，直接覆盖为 value
    """
    data = read_yaml(file_path)
    if key not in data:
        data[key] = []
    if isinstance(data[key], list):
        data[key].append(value)
    else:
        data[key] = value
    _save_yaml(file_path, data)


def clear_yaml(file_path=EXTRACT_PATH):
    """清空 YAML 文件内容（文件本身保留）"""
    with open(file_path, "w", encoding="utf-8") as f:
        pass


def _save_yaml(file_path, data):
    """内部方法：将字典数据写入 YAML 文件（自动创建目录）"""
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
