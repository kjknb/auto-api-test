# ============================================================
# conftest.py
# Pytest 全局配置 —— 定义 session 级 Fixture 和测试生命周期钩子
# 这是整个测试框架的"启动器"，负责初始化环境、创建请求客户端
# ============================================================

import os
import pytest
import shutil
from datetime import datetime

from common.yaml_util import read_yaml
from common.request_util import RequestUtil
from common.logger import get_logger

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(ROOT_DIR, "config", "config.yaml")

logger = get_logger("conftest")


# ============================================================
# 测试生命周期钩子
# ============================================================

def pytest_sessionstart(session):
    """
    测试会话开始时执行（整个测试跑之前）
    职责：
    1. 清空 extract.yaml —— 每次测试都是全新开始
    2. 清空并重建 Allure 报告目录
    3. 确保日志目录存在
    """
    base = os.path.dirname(__file__)

    # 清空用例间传递数据的 extract.yaml
    extract = os.path.join(base, "extract.yaml")
    if os.path.exists(extract):
        open(extract, "w").close()
        logger.info(f"已清空上下文文件: {extract}")

    # 重建 Allure 报告目录（每次测试生成全新报告）
    for d in ["reports/allure-results", "reports/allure-report"]:
        path = os.path.join(base, d)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

    # 确保日志目录存在
    os.makedirs(os.path.join(base, "reports", "logs"), exist_ok=True)


# ============================================================
# Session 级 Fixture（整个测试会话共享同一实例）
# ============================================================

@pytest.fixture(scope="session")
def config():
    """
    加载 config/config.yaml 配置文件
    - scope=session：整个测试会话只加载一次
    - 返回字典，包含环境配置、登录配置等
    """
    return read_yaml(CONFIG_FILE)


@pytest.fixture(scope="session")
def base_url(config):
    """
    根据当前环境获取 API 根地址
    - 从 config.env 确定环境（dev/test/prod）
    - 从 env_config 对应环境取 base_url
    """
    env = config.get("env", "test")
    url = config.get("env_config", {}).get(env, {}).get("base_url", "http://localhost:8080")
    logger.info(f"当前环境: {env} -> {url}")
    return url


@pytest.fixture(scope="session")
def request_util(base_url) -> RequestUtil:
    """
    创建全局 HTTP 请求客户端
    - scope=session：所有用例共享同一个 Session（复用 TCP 连接）
    - 测试结束后自动关闭连接
    """
    req = RequestUtil(base_url=base_url)
    yield req          # yield 之后的代码在测试结束后执行
    req.close()


@pytest.fixture(scope="session")
def user_api(request_util):
    """
    创建用户模块 API 封装实例
    - 注入 request_util，所有用户接口都通过这个实例调用
    """
    from api.user_api import UserApi
    return UserApi(request_util)


# ============================================================
# 数据驱动参数化（从 data/user_data.yaml 读取测试数据）
# 工作原理：
#   pytest 收集用例时，根据用例所在文件名匹配 yaml 中的数据段
#   test_01_register.py → register 段
#   test_02_login.py    → login 段
#   test_04_update.py   → update 段
# 用例只需定义 def test_xxx(self, user_api, case): ，case 由这里自动注入
# ============================================================

# 文件名到 yaml 数据段的映射
_DATA_MAP = {
    "test_01_register": "register",
    "test_02_login": "login",
    "test_04_update": "update",
}

# 缓存测试数据（整个会话只读一次 yaml）
_test_data_cache = None


def _get_test_data():
    """懒加载测试数据，避免重复读取文件"""
    global _test_data_cache
    if _test_data_cache is None:
        data_file = os.path.join(ROOT_DIR, "data", "user_data.yaml")
        _test_data_cache = read_yaml(data_file)
    return _test_data_cache


def pytest_generate_tests(metafunc):
    """
    Pytest 钩子：为包含 `case` 参数的用例自动生成参数化
    - 根据用例所在文件名找到 yaml 中对应的数据段
    - 每条数据展开为一个独立用例
    - ids 用 title 字段，报告显示中文名称
    """
    # 只对有 case 参数的用例做参数化
    if "case" not in metafunc.fixturenames:
        return

    # 根据文件名找对应的数据段（如 test_01_register → register）
    filename = os.path.splitext(os.path.basename(metafunc.module.__file__))[0]
    data_key = _DATA_MAP.get(filename)
    if not data_key:
        return

    test_data = _get_test_data()
    cases = test_data.get(data_key, [])
    if not cases:
        return

    # 注入参数化：每个 case 字典展开为一个用例，title 作为用例名称
    metafunc.parametrize("case", cases, ids=[c.get("title", f"case_{i}") for i, c in enumerate(cases)])


# ============================================================
# 测试用例日志分隔（让日志更容易阅读）
# ============================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_setup(item):
    """每个用例开始前打印分隔线"""
    logger.info(f"\n{'='*60}")
    logger.info(f"[TEST START] {item.name} - {datetime.now().strftime('%H:%M:%S')}")
    logger.info(f"{'='*60}")
    yield


@pytest.hookimpl(trylast=True, hookwrapper=True)
def pytest_runtest_teardown(item):
    """每个用例结束后打印分隔线"""
    yield
    logger.info(f"{'='*60}")
    logger.info(f"[TEST END] {item.name}")
    logger.info(f"{'='*60}\n")
