# ============================================================
# testcases/test_01_register.py
# 注册接口测试 —— 验证用户注册的各种场景
# 测试数据来源：data/user_data.yaml → register 段
# 参数化方式：conftest.py 的 pytest_generate_tests 钩子自动注入
# ============================================================

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.context_util import save_context


@pytest.mark.dependency(name="register", scope="session")
class TestRegister:
    """注册接口测试类"""

    def test_register(self, user_api: UserApi, case):
        """
        用户注册测试（数据驱动）
        - 数据由 conftest.py 从 data/user_data.yaml 的 register 段读取
        - 每条数据自动展开为一个独立用例
        - 注册成功时保存用户信息到上下文（供后续登录用例使用）
        """
        print(f"\n📝 测试: {case['title']}")

        # 发起注册请求
        resp = user_api.register(case["username"], case["password"])

        # 断言 HTTP 状态码
        AssertUtil.assert_status_code(resp, 200)
        # 断言业务状态码
        AssertUtil.assert_code(resp, case["expected_code"])

        # 注册成功时，保存用户信息到上下文（test_02_login 会用到）
        if case["expected_code"] == 0:
            body = resp.json()
            user_info = {
                "id": body.get("data", {}).get("id"),
                "username": case["username"],
                "password": case["password"],
            }
            save_context("current_user", user_info)
            print(f"✅ 注册成功，用户信息已保存: {user_info}")
