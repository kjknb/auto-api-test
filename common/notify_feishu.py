# ============================================================
# common/notify_feishu.py
# 飞书群通知工具 —— 测试完成后自动发送结果到飞书群
# Webhook URL 从环境变量 FEISHU_WEBHOOK_URL 读取（不存明文）
# 也可作为独立脚本运行：python common/notify_feishu.py "通知内容"
# ============================================================

import os
import sys
import json
import requests
from common.logger import get_logger

# 环境变量名（飞书 Webhook 地址）
WEBHOOK_ENV = "FEISHU_WEBHOOK_URL"

logger = get_logger("FeishuNotify")


def send_feishu_msg(message: str, at_all: bool = False):
    """
    发送飞书群通知
    :param message: 通知文本内容
    :param at_all: 是否 @所有人（紧急通知时使用）
    """
    webhook_url = os.environ.get(WEBHOOK_ENV, "")

    # 没有配置 Webhook 时静默跳过（不影响测试流程）
    if not webhook_url:
        logger.warning(f"环境变量 {WEBHOOK_ENV} 未设置，跳过飞书通知")
        return

    try:
        # 如果需要 @所有人，拼接 at 标签
        mention = '<at user_id="all">所有人</at>\n' if at_all else ""
        payload = {
            "msg_type": "text",
            "content": {"text": f"{mention}{message}"},
        }

        logger.info(f"发送飞书通知: {message}")
        resp = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10,
        )

        if resp.status_code == 200:
            logger.info("飞书通知发送成功")
        else:
            logger.warning(f"飞书通知失败: HTTP {resp.status_code}")

    except Exception as e:
        logger.error(f"飞书通知异常: {e}")


# 支持命令行直接调用：python common/notify_feishu.py "测试完成"
if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "自动化测试完成"
    send_feishu_msg(msg, at_all=True)
