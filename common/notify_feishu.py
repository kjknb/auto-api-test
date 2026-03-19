# common/notify_feishu.py
"""飞书通知工具 —— 从环境变量读取 Webhook URL"""

import os
import sys
import json
import traceback
import requests

WEBHOOK_ENV = "FEISHU_WEBHOOK_URL"


def send_feishu_msg(message: str, at_all: bool = False):
    """
    发送飞书群通知
    :param message: 通知内容
    :param at_all: 是否 @所有人
    """
    webhook_url = os.environ.get(WEBHOOK_ENV, "")

    if not webhook_url:
        print(f"[WARN] 环境变量 {WEBHOOK_ENV} 未设置，跳过飞书通知")
        return

    try:
        mention = '<at user_id="all">所有人</at>\n' if at_all else ""
        payload = {
            "msg_type": "text",
            "content": {"text": f"{mention}{message}"},
        }

        print(f"🚀 发送飞书通知: {message}")
        resp = requests.post(
            webhook_url, headers={"Content-Type": "application/json"},
            data=json.dumps(payload), timeout=10
        )

        if resp.status_code == 200:
            print("✅ 飞书通知发送成功")
        else:
            print(f"⚠️ 飞书通知失败: HTTP {resp.status_code}")

    except Exception as e:
        print(f"❌ 飞书通知异常: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "🔔 自动化测试完成"
    send_feishu_msg(msg, at_all=True)
