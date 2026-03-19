# common/token_util.py
import os
import yaml
from common.logger import get_logger

logger = get_logger("TokenUtil")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, "config", "token.yaml")


def save_token(token_value: str):
    """保存 Token 到 config/token.yaml"""
    if not token_value:
        logger.warning("Token 为空，不写入")
        return
    data = {"token": token_value}
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True)
    logger.info(f"Token 已保存到 {TOKEN_FILE}")


def read_token() -> str:
    """从 config/token.yaml 读取 Token"""
    if not os.path.exists(TOKEN_FILE):
        logger.warning(f"Token 文件不存在: {TOKEN_FILE}")
        return ""
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("token", "")
