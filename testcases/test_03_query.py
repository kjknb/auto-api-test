# ============================================================
# testcases/test_03_query.py
# 查询接口测试 —— 验证用户查询功能
# 依赖 test_02_login（需要 Token 鉴权才能访问）
# ============================================================

import pytest
from api.user_api import UserApi
from common.assert_util import AssertUtil
from common.context_util import get_context


@pytest.mark.dependency(name="query", depends=["login"], scope="session")
class TestQuery:
    """查询接口测试类（需要登录后的 Token）"""

    def test_get_user_list(self, user_api: UserApi):
        """
        查询用户列表
        - 请求 GET /user/list
        - 断言返回的 data 字段不为空（至少有一个用户）
        """
        print("\n📝 测试: 查询用户列表")

        resp = user_api.get_user()
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, 0)
        AssertUtil.assert_not_empty(resp, "data")

        users = resp.json().get("data", [])
        print(f"✅ 查询成功，共 {len(users)} 个用户")

    def test_get_user_by_id(self, user_api: UserApi):
        """
        根据 ID 查询单个用户
        - 从上下文中读取注册时保存的 user_id
        - 如果没有 user_id（注册失败），跳过此用例
        """
        print("\n📝 测试: 根据 ID 查询用户")

        # 从上下文获取之前注册的用户 ID
        user = get_context("current_user", {})
        user_id = user.get("id")
        if not user_id:
            pytest.skip("无可用用户 ID（注册可能失败了）")

        resp = user_api.get_user(user_id)
        AssertUtil.assert_status_code(resp, 200)
        AssertUtil.assert_code(resp, 0)
        print(f"✅ 查询成功: {resp.json()}")
