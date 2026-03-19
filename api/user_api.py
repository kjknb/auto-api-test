# api/user_api.py
"""用户接口封装 —— 注册、登录、查询、更新、删除"""

from common.request_util import RequestUtil


class UserApi:
    """用户模块 API 封装"""

    def __init__(self, request_util: RequestUtil):
        self.req = request_util

    def register(self, username: str, password: str):
        """注册"""
        return self.req.post("/user/register", json={
            "username": username,
            "password": password,
        })

    def login(self, username: str, password: str):
        """登录"""
        return self.req.post("/user/login", json={
            "username": username,
            "password": password,
        })

    def get_user(self, user_id: int = None):
        """查询用户（单个或列表）"""
        if user_id:
            return self.req.get(f"/user/{user_id}")
        return self.req.get("/user/list")

    def update_user(self, user_id: int, **kwargs):
        """更新用户信息"""
        data = {"id": user_id}
        data.update(kwargs)
        return self.req.put("/user/update", json=data)

    def delete_user(self, user_id: int):
        """删除用户"""
        return self.req.delete("/user/delete", params={"id": user_id})
