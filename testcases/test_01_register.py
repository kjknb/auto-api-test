# ============================================================
# testcases/test_01_register.py
# 注册接口测试 —— 验证用户注册的各种场景
# 测试数据从 data/user_data.yaml 中的 register 段读取
# ============================================================

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.context_util import save_context


@pytest.mark.dependency(name="register", scope="session")
class TestRegister:
    """注册接口测试类"""

    @pytest.mark.parametrize("case", [
        # ---- 正向用例：正常注册应该成功 ----
        {"title": "正常注册", "username": "test_user_001", "password": "123456", "expected_code": 0},
        # ---- 反向用例：重复注册应该返回"用户已存在" ----
        {"title": "重复注册", "username": "test_user_001", "password": "123456", "expected_code": 1001},
        # ---- 反向用例：空用户名应该返回"用户名不能为空" ----
        {"title": "空用户名", "username": "", "password": "123456", "expected_code": 1002},
    ], ids=lambda c: c["title"])   # 用例标题显示为中文，而不是默认的 test_register[0]
    def test_register(self, user_api: UserApi, case):
        """
        用户注册测试
        - 请求 POST /user/register
        - 断言 HTTP 状态码 200
        - 断言业务码与预期一致
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
