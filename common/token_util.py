# ============================================================
# common/token_util.py
# Token 管理工具 —— 登录后保存 Token，后续请求自动携带
# Token 存储在 config/token.yaml（已在 .gitignore 中排除）
# ============================================================

import os
import yaml
from common.logger import get_logger

logger = get_logger("TokenUtil")

# Token 存储文件路径（项目根目录下的 config/token.yaml）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, "config", "token.yaml")


def save_token(token_value: str):
    """
    保存 Token 到本地文件
    - 通常在登录成功后调用
    - 空字符串不会写入（避免覆盖已有有效 Token）
    """
    if not token_value:
        logger.warning("Token 为空，不写入")
        return
    data = {"token": token_value}
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True)
    logger.info(f"Token 已保存到 {TOKEN_FILE}")


def read_token() -> str:
    """
    从本地文件读取 Token
    - 文件不存在时返回空字符串
    - 用于需要手动设置请求头的场景
    """
    if not os.path.exists(TOKEN_FILE):
        logger.warning(f"Token 文件不存在: {TOKEN_FILE}")
        return ""
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("token", "")
