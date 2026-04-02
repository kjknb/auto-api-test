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


@pytest.fixture(scope="session")
def test_data():
    """
    加载测试数据（data/user_data.yaml）
    - 数据驱动测试的基础，用例从这里读取参数化数据
    """
    data_file = os.path.join(ROOT_DIR, "data", "user_data.yaml")
    return read_yaml(data_file)


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
