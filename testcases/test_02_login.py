# ============================================================
# testcases/test_02_login.py
# 登录接口测试 —— 验证用户登录的各种场景
# 依赖 test_01_register（必须先注册再登录）
# 登录成功后保存 Token，供后续需要鉴权的接口使用
# ============================================================

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.token_util import save_token
from common.context_util import get_context, save_context


@pytest.mark.dependency(name="login", depends=["register"], scope="session")
class TestLogin:
    """登录接口测试类（依赖注册成功）"""

    @pytest.mark.parametrize("case", [
        # ---- 正向用例：正确账号密码应该登录成功 ----
        {"title": "正确登录", "username": "test_user_001", "password": "123456", "expected_code": 0},
        # ---- 反向用例：错误密码应该返回"密码错误" ----
        {"title": "错误密码", "username": "test_user_001", "password": "wrong", "expected_code": 1003},
        # ---- 反向用例：不存在的用户应该返回"用户不存在" ----
        {"title": "不存在的用户", "username": "non_exist_user", "password": "123456", "expected_code": 1004},
    ], ids=lambda c: c["title"])
    def test_login(self, user_api: UserApi, case):
        """
        用户登录测试
        - 请求 POST /user/login
        - 断言 HTTP 状态码和业务码
        - 登录成功时：保存 Token + 更新请求头（后续接口自动带鉴权）
        """
        print(f"\n📝 测试: {case['title']}")

        # 发起登录请求
        resp = user_api.login(case["username"], case["password"])

        # 断言
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, case["expected_code"])

        # 登录成功时，做三件事：
        # 1. 保存 Token 到文件
        # 2. 更新全局请求头（后续所有请求自动携带 Authorization）
        # 3. 更新上下文中的用户信息
        if case["expected_code"] == 0:
            body = resp.json()
            token = body.get("data", {}).get("token", "")
            if token:
                save_token(token)
                user_api.req.update_headers({"Authorization": f"Bearer {token}"})
                print("✅ 登录成功，Token 已保存并更新请求头")

                # 把 Token 也存到用户上下文中
                user = get_context("current_user", {})
                user["token"] = token
                save_context("current_user", user)
