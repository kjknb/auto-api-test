"""
mock_server.py —— 模拟后端 API，用于本地验证测试框架
启动后监听 localhost:8080，提供 /user/register、/user/login 等接口
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid

# 模拟数据库
users_db = {}
next_id = 1


class MockHandler(BaseHTTPRequestHandler):
    """处理所有 API 请求的 Handler"""

    def log_message(self, format, *args):
        """抑制默认日志输出"""
        pass

    def _send_json(self, status, body):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def _read_body(self):
        """读取请求体"""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_POST(self):
        body = self._read_body()

        if self.path == "/user/register":
            username = body.get("username", "")
            password = body.get("password", "")

            # 空用户名校验
            if not username:
                return self._send_json(200, {"code": 1002, "msg": "用户名不能为空"})

            # 重复注册校验
            for u in users_db.values():
                if u["username"] == username:
                    return self._send_json(200, {"code": 1001, "msg": "用户已存在"})

            # 正常注册
            global next_id
            user_id = next_id
            next_id += 1
            users_db[user_id] = {"id": user_id, "username": username, "password": password}
            return self._send_json(200, {"code": 0, "msg": "注册成功", "data": {"id": user_id}})

        elif self.path == "/user/login":
            username = body.get("username", "")
            password = body.get("password", "")

            # 查找用户
            target = None
            for u in users_db.values():
                if u["username"] == username:
                    target = u
                    break

            if not target:
                return self._send_json(200, {"code": 1004, "msg": "用户不存在"})

            if target["password"] != password:
                return self._send_json(200, {"code": 1003, "msg": "密码错误"})

            # 登录成功，返回 Token
            token = f"token_{uuid.uuid4().hex[:16]}"
            return self._send_json(200, {"code": 0, "msg": "登录成功", "data": {"token": token}})

        else:
            self._send_json(404, {"code": -1, "msg": "Not Found"})

    def do_PUT(self):
        body = self._read_body()

        if self.path == "/user/update":
            user_id = body.get("id")
            if user_id and user_id in users_db:
                users_db[user_id].update({k: v for k, v in body.items() if k != "id"})
                return self._send_json(200, {"code": 0, "msg": "更新成功"})
            return self._send_json(200, {"code": 1005, "msg": "用户不存在"})

        self._send_json(404, {"code": -1, "msg": "Not Found"})

    def do_GET(self):
        if self.path == "/user/list":
            user_list = [{"id": u["id"], "username": u["username"]} for u in users_db.values()]
            return self._send_json(200, {"code": 0, "msg": "查询成功", "data": user_list})

        # /user/{id}
        if self.path.startswith("/user/"):
            try:
                uid = int(self.path.split("/")[-1])
                if uid in users_db:
                    u = users_db[uid]
                    return self._send_json(200, {"code": 0, "msg": "查询成功", "data": u})
                return self._send_json(200, {"code": 1004, "msg": "用户不存在"})
            except ValueError:
                pass

        self._send_json(404, {"code": -1, "msg": "Not Found"})

    def do_DELETE(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)

        if parsed.path == "/user/delete":
            params = parse_qs(parsed.query)
            uid_str = params.get("id", [None])[0]
            if uid_str:
                uid = int(uid_str)
                if uid in users_db:
                    del users_db[uid]
                    return self._send_json(200, {"code": 0, "msg": "删除成功"})
                return self._send_json(200, {"code": 1004, "msg": "用户不存在"})

        self._send_json(404, {"code": -1, "msg": "Not Found"})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), MockHandler)
    print("🚀 Mock API Server running on http://localhost:8080")
    server.serve_forever()
