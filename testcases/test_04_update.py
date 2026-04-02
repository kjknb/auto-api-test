# ============================================================
# testcases/test_04_update.py
# 更新接口测试 —— 验证用户信息修改功能
# 依赖 test_02_login（需要 Token 鉴权）
# ============================================================

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.context_util import get_context, save_context


@pytest.mark.dependency(name="update", depends=["login"], scope="session")
class TestUpdate:
    """更新接口测试类（需要登录后的 Token）"""

    def test_update_username(self, user_api: UserApi):
        """
        更新用户名
        - 在原用户名后拼接 _updated
        - 更新成功后同步修改上下文中的用户名
        """
        print("\n📝 测试: 更新用户名")

        user = get_context("current_user", {})
        user_id = user.get("id")
        if not user_id:
            pytest.skip("无可用用户 ID")

        new_name = user.get("username", "") + "_updated"
        resp = user_api.update_user(user_id, username=new_name)
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, 0)

        # 同步更新上下文（保持数据一致）
        user["username"] = new_name
        save_context("current_user", user)
        print(f"✅ 更新成功，新用户名: {new_name}")

    def test_update_phone(self, user_api: UserApi):
        """
        更新手机号
        - 设置新手机号，验证接口返回成功
        """
        print("\n📝 测试: 更新手机号")

        user = get_context("current_user", {})
        user_id = user.get("id")
        if not user_id:
            pytest.skip("无可用用户 ID")

        resp = user_api.update_user(user_id, phone="13800138000")
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, 0)
        print("✅ 手机号更新成功")
