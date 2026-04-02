# ============================================================
# testcases/test_05_delete.py
# 删除接口测试 —— 验证用户删除功能
# 依赖 test_04_update（删除是 CRUD 最后一步）
# ============================================================

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.context_util import get_context


@pytest.mark.dependency(name="delete", depends=["update"], scope="session")
class TestDelete:
    """删除接口测试类（CRUD 流程的最后一步）"""

    def test_delete_user(self, user_api: UserApi):
        """
        正常删除用户
        - 用之前注册的用户 ID 删除
        - 验证返回业务码为 0（成功）
        """
        print("\n📝 测试: 删除用户")

        user = get_context("current_user", {})
        user_id = user.get("id")
        if not user_id:
            pytest.skip("无可用用户 ID")

        resp = user_api.delete_user(user_id)
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, 0)
        print(f"✅ 用户 {user.get('username')} (id={user_id}) 删除成功")

    def test_delete_non_exist(self, user_api: UserApi):
        """
        删除不存在的用户（反向用例）
        - 使用一个不可能存在的 ID (999999)
        - 验证接口返回"用户不存在"的业务码
        """
        print("\n📝 测试: 删除不存在的用户")

        resp = user_api.delete_user(999999)
        AssertUtil.assert_status_code(resp, 200)

        # 断言业务码不为 0（删除不存在的用户应该报错）
        body = resp.json()
        code = body.get("code")
        print(f"✅ 接口响应: {body}")
        assert code != 0, f"删除不存在的用户应该返回非 0 业务码，实际: {code}"
