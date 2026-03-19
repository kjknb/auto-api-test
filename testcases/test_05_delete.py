# testcases/test_05_delete.py
"""删除接口测试"""

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.context_util import get_context


@pytest.mark.dependency(name="delete", depends=["update"], scope="session")
class TestDelete:

    def test_delete_user(self, user_api: UserApi):
        """删除用户"""
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
        """删除不存在的用户"""
        print("\n📝 测试: 删除不存在的用户")

        resp = user_api.delete_user(999999)
        AssertUtil.assert_status_code(resp, 200)
        # 业务码应为非 0（用户不存在）
        body = resp.json()
        print(f"✅ 接口响应: {body}")
