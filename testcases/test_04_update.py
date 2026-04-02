# ============================================================
# testcases/test_04_update.py
# 更新接口测试 —— 验证用户信息修改功能
# 测试数据来源：data/user_data.yaml → update 段
# 依赖 test_02_login（需要 Token 鉴权）
# ============================================================

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.context_util import get_context, save_context


@pytest.mark.dependency(name="update", depends=["login"], scope="session")
class TestUpdate:
    """更新接口测试类（需要登录后的 Token）"""

    def test_update(self, user_api: UserApi, case):
        """
        用户信息更新测试（数据驱动）
        - 数据由 conftest.py 从 data/user_data.yaml 的 update 段读取
        - 每条数据是一个 field + value 组合，动态构造更新请求
        """
        print(f"\n📝 测试: {case['title']}")

        # 从上下文获取当前用户 ID
        user = get_context("current_user", {})
        user_id = user.get("id")
        if not user_id:
            pytest.skip("无可用用户 ID")

        # 用 yaml 中的 field 和 value 动态构造更新请求
        resp = user_api.update_user(user_id, **{case["field"]: case["value"]})
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, case["expected_code"])

        # 更新成功时同步上下文
        if case["expected_code"] == 0:
            user[case["field"]] = case["value"]
            save_context("current_user", user)
            print(f"✅ 更新成功: {case['field']} = {case['value']}")
