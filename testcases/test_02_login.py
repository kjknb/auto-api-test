# testcases/test_02_login.py
"""登录接口测试"""

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.token_util import save_token
from common.context_util import get_context, save_context


@pytest.mark.dependency(name="login", depends=["register"], scope="session")
class TestLogin:

    @pytest.mark.parametrize("case", [
        {"title": "正确登录", "username": "test_user_001", "password": "123456", "expected_code": 0},
        {"title": "错误密码", "username": "test_user_001", "password": "wrong", "expected_code": 1003},
        {"title": "不存在的用户", "username": "non_exist_user", "password": "123456", "expected_code": 1004},
    ], ids=lambda c: c["title"])
    def test_login(self, user_api: UserApi, case):
        """用户登录"""
        print(f"\n📝 测试: {case['title']}")

        resp = user_api.login(case["username"], case["password"])
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, case["expected_code"])

        # 登录成功时保存 Token
        if case["expected_code"] == 0:
            body = resp.json()
            token = body.get("data", {}).get("token", "")
            if token:
                save_token(token)
                # 更新请求头
                user_api.req.update_headers({"Authorization": f"Bearer {token}"})
                print("✅ 登录成功，Token 已保存")

                # 更新用户信息中的 token
                user = get_context("current_user", {})
                user["token"] = token
                save_context("current_user", user)
