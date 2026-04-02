# ============================================================
# api/user_api.py
# 用户模块 API 封装 —— 把所有用户相关的 HTTP 请求集中管理
# 测试用例只调用方法，不用关心 URL、请求体结构等细节
# 新增接口只需在这里加方法，在 testcases/ 下加对应用例
# ============================================================

from common.request_util import RequestUtil


class UserApi:
    """
    用户模块 API 集合
    每个方法对应一个接口，返回 requests.Response 对象
    """

    def __init__(self, request_util: RequestUtil):
        # 注入全局请求工具，复用 Session 和全局 Headers
        self.req = request_util

    def register(self, username: str, password: str):
        """POST /user/register — 用户注册"""
        return self.req.post("/user/register", json={
            "username": username,
            "password": password,
        })

    def login(self, username: str, password: str):
        """POST /user/login — 用户登录（成功后返回 Token）"""
        return self.req.post("/user/login", json={
            "username": username,
            "password": password,
        })

    def get_user(self, user_id: int = None):
        """
        GET /user/{id} 或 /user/list — 查询用户
        - 传 user_id：查询单个用户详情
        - 不传 user_id：查询用户列表
        """
        if user_id:
            return self.req.get(f"/user/{user_id}")
        return self.req.get("/user/list")

    def update_user(self, user_id: int, **kwargs):
        """PUT /user/update — 更新用户信息（可传任意字段）"""
        data = {"id": user_id}
        data.update(kwargs)
        return self.req.put("/user/update", json=data)

    def delete_user(self, user_id: int):
        """DELETE /user/delete — 根据 ID 删除用户"""
        return self.req.delete("/user/delete", params={"id": user_id})
