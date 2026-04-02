# ============================================================
# common/logger.py
# 统一日志工具 —— 同时输出到控制台（带颜色）和文件（自动轮转）
# 所有模块通过 get_logger(name) 获取 logger 实例
# ============================================================

import logging
import os
from logging.handlers import RotatingFileHandler

# 尝试导入 colorlog（可选依赖，没有也能正常运行）
try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

# 控制台日志颜色映射
LOG_COLORS = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


def get_logger(name: str = "api_test") -> logging.Logger:
    """
    获取一个配置好的 logger 实例（控制台 + 文件双输出）
    - 控制台：INFO 级别，带颜色（需 colorlog）
    - 文件：DEBUG 级别，自动轮转（10MB/文件，最多保留 5 个）
    - 日志路径：reports/logs/test.log
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler（多次调用 get_logger 不会重复输出）
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ---- 确定日志目录 ----
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(root_dir, "reports", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "test.log")

    # ---- 文件 handler：详细日志，方便排查问题 ----
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    # ---- 控制台 handler：简洁输出，带颜色高亮 ----
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    if HAS_COLORLOG:
        console_fmt = colorlog.ColoredFormatter(
            fmt="%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            log_colors=LOG_COLORS,
        )
    else:
        console_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )
    console.setFormatter(console_fmt)
    logger.addHandler(console)

    return logger


# 模块级默认 logger，可直接 from common.logger import logger 使用
logger = get_logger()
