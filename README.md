# Auto API Test

通用 API 自动化测试框架，基于 Pytest + Allure + Jenkins。

## 功能

- 🧪 接口自动化测试（注册、登录、CRUD 模板）
- 📊 数据驱动 —— 测试数据从 YAML 读取，改数据不改代码
- 📊 Allure 测试报告
- 🐳 Docker + docker-compose 一键部署
- 🔄 Jenkins CI/CD 流水线
- 📢 飞书通知
- 🌍 多环境配置（dev / test / prod）
- 🔐 Token 自动管理 + 敏感信息脱敏

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制并修改配置（config.yaml 不入库，需要手动创建）
cp config/config.yaml.example config/config.yaml

# 3. 启动后端服务（或用 mock 服务器测试）
# python mock_server.py

# 4. 运行测试
pytest -s -v

# 5. 查看 Allure 报告
allure serve reports/allure-results
```

## 数据驱动

测试用例的数据从 `data/user_data.yaml` 读取，通过 `conftest.py` 中的 `pytest_generate_tests` 钩子自动注入。

### 工作原理

```
data/user_data.yaml                     conftest.py
├── register:                           pytest_generate_tests(metafunc):
│   - title: "正常注册"                     ↓ 根据用例文件名找对应数据段
│     username: "test_user_001"            ↓ metafunc.parametrize("case", cases)
│     password: "123456"                   ↓ 每条数据展开为一个用例
│     expected_code: 0                     ↓
├── login:                              testcases/test_01_register.py
│   - title: "正确登录"                    def test_register(self, user_api, case):
└── update:                                    ↑ case 自动注入
    - title: "更新用户名"
```

### 文件名 → 数据段映射

| 测试文件 | 数据段 |
|---------|--------|
| `test_01_register.py` | `register` |
| `test_02_login.py` | `login` |
| `test_04_update.py` | `update` |

**新增测试场景只需改 YAML，不用动测试代码。**

## 项目结构

```
auto-api-test/
├── config/
│   ├── config.yaml.example   # 配置模板（提交到仓库）
│   ├── config.yaml           # 实际配置（.gitignore 忽略）
│   └── token.yaml            # Token 缓存（自动生成，不入库）
├── common/                   # 基础工具层
│   ├── request_util.py       # HTTP 请求封装（Session、日志、脱敏）
│   ├── yaml_util.py          # YAML 读写工具
│   ├── logger.py             # 日志工具（控制台彩色 + 文件轮转）
│   ├── assert_util.py        # 断言封装（状态码、业务码、JSON 路径）
│   ├── token_util.py         # Token 管理（保存/读取）
│   ├── context_util.py       # 上下文传递（用例间数据共享）
│   └── notify_feishu.py      # 飞书通知
├── api/                      # 接口封装层
│   ├── __init__.py
│   └── user_api.py           # 用户接口封装（CRUD）
├── data/                     # 测试数据层
│   └── user_data.yaml        # 测试数据（注册、登录、更新场景）
├── testcases/                # 测试用例层
│   ├── __init__.py
│   ├── test_01_register.py   # 注册测试（数据驱动）
│   ├── test_02_login.py      # 登录测试（数据驱动）
│   ├── test_03_query.py      # 查询测试
│   ├── test_04_update.py     # 更新测试（数据驱动）
│   └── test_05_delete.py     # 删除测试
├── scripts/
│   └── run.sh                # 本地运行脚本
├── mock_server.py            # Mock 后端（本地验证用）
├── reports/                  # 测试报告（gitignore）
├── Dockerfile                # 被测服务镜像（按实际项目修改）
├── Dockerfile.jenkins        # Jenkins 镜像（预装 Python + Allure）
├── docker-compose.yml        # 一键启动所有服务
├── Jenkinsfile               # CI/CD 流水线
├── conftest.py               # Pytest 全局 Fixture + 参数化钩子
├── pytest.ini                # Pytest 配置
└── requirements.txt          # Python 依赖
```

## 切换环境

修改 `config/config.yaml` 中的 `env` 字段：

```yaml
env: test  # dev / test / prod
```

## 添加新接口测试

1. 在 `api/` 下新增接口封装类（参考 `user_api.py`）
2. 在 `data/` 下准备测试数据
3. 在 `testcases/` 下编写测试用例，定义 `def test_xxx(self, user_api, case):`
4. 在 `conftest.py` 的 `_DATA_MAP` 中添加文件名到数据段的映射

## 配置安全

- `config/config.yaml` 不提交到仓库（.gitignore 已排除）
- 首次使用：`cp config/config.yaml.example config/config.yaml`
- 敏感信息通过环境变量注入
- 飞书 Webhook 通过 `FEISHU_WEBHOOK_URL` 环境变量配置

## Jenkins

项目已配置 Jenkinsfile，push 到 main 分支自动触发构建。
流水线：Checkout → Install → Test → Report → 飞书通知

## License

MIT
