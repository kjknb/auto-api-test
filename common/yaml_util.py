# common/yaml_util.py
import os
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT_PATH = os.path.join(BASE_DIR, "extract.yaml")


def read_yaml(file_path: str):
    """读取 YAML 文件"""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(key, value, file_path=EXTRACT_PATH):
    """写入指定 key 到 YAML 文件"""
    data = read_yaml(file_path)
    data[key] = value
    _save_yaml(file_path, data)


def append_yaml(key, value, file_path=EXTRACT_PATH):
    """追加值到 YAML 中的列表 key"""
    data = read_yaml(file_path)
    if key not in data:
        data[key] = []
    if isinstance(data[key], list):
        data[key].append(value)
    else:
        data[key] = value
    _save_yaml(file_path, data)


def clear_yaml(file_path=EXTRACT_PATH):
    """清空 YAML 文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        pass  # "w" 模式已自动截断文件


def _save_yaml(file_path, data):
    """内部方法：保存数据到 YAML"""
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
