# testcases/test_01_register.py
"""注册接口测试"""

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.context_util import save_context


@pytest.mark.dependency(name="register", scope="session")
class TestRegister:

    @pytest.mark.parametrize("case", [
        {"title": "正常注册", "username": "test_user_001", "password": "123456", "expected_code": 0},
        {"title": "重复注册", "username": "test_user_001", "password": "123456", "expected_code": 1001},
        {"title": "空用户名", "username": "", "password": "123456", "expected_code": 1002},
    ], ids=lambda c: c["title"])
    def test_register(self, user_api: UserApi, case):
        """用户注册"""
        print(f"\n📝 测试: {case['title']}")

        resp = user_api.register(case["username"], case["password"])
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, case["expected_code"])

        # 注册成功时保存用户信息
        if case["expected_code"] == 0:
            body = resp.json()
            user_info = {
                "id": body.get("data", {}).get("id"),
                "username": case["username"],
                "password": case["password"],
            }
            save_context("current_user", user_info)
            print(f"✅ 注册成功: {user_info}")
