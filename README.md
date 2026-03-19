# Auto API Test

通用 API 自动化测试框架，基于 Pytest + Allure + Jenkins。

## 功能

- 🧪 接口自动化测试（注册、登录、CRUD 模板）
- 📊 Allure 测试报告
- 🐳 Docker + docker-compose 一键部署
- 🔄 Jenkins CI/CD 流水线
- 📢 飞书通知
- 🌍 多环境配置（dev / test / prod）
- 🔐 Token 自动管理

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 修改配置
cp config/config.yaml config/config.yaml  # 按需修改

# 3. 运行测试
pytest -s -v

# 4. 查看 Allure 报告
allure serve reports/allure-results
```

## 项目结构

```
auto-api-test/
├── config/
│   ├── config.yaml          # 多环境配置
│   └── token.yaml           # Token 缓存（自动生成）
├── common/
│   ├── request_util.py      # HTTP 请求封装
│   ├── yaml_util.py         # YAML 读写工具
│   ├── logger.py            # 日志工具
│   ├── assert_util.py       # 断言封装
│   ├── token_util.py        # Token 管理
│   ├── context_util.py      # 上下文传递
│   └── notify_feishu.py     # 飞书通知
├── api/
│   ├── __init__.py
│   └── user_api.py          # 用户接口封装
├── data/
│   └── user_data.yaml       # 测试数据
├── testcases/
│   ├── __init__.py
│   ├── test_01_register.py  # 注册
│   ├── test_02_login.py     # 登录
│   ├── test_03_query.py     # 查询
│   ├── test_04_update.py    # 更新
│   └── test_05_delete.py    # 删除
├── scripts/
│   └── run.sh               # 运行脚本
├── reports/                 # 测试报告（gitignore）
├── Dockerfile               # 被测服务示例
├── Dockerfile.jenkins       # Jenkins 镜像
├── docker-compose.yml       # 一键启动
├── Jenkinsfile              # CI/CD 流水线
├── conftest.py              # Pytest 全局配置
├── pytest.ini               # Pytest 配置
└── requirements.txt
```

## 切换环境

修改 `config/config.yaml` 中的 `env` 字段：

```yaml
env: test  # dev / test / prod
```

## 添加新接口测试

1. 在 `api/` 下新增接口封装类
2. 在 `data/` 下准备测试数据
3. 在 `testcases/` 下编写测试用例

## Jenkins

项目已配置 Jenkinsfile，push 到 main 分支自动触发构建。

## License

MIT
