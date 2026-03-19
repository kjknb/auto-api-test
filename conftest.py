# conftest.py
# Pytest 全局配置

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


# ==================== 初始化 ====================

def pytest_sessionstart(session):
    """测试会话开始：清空 extract.yaml 和 Allure 报告"""
    base = os.path.dirname(__file__)

    # 清空 extract.yaml
    extract = os.path.join(base, "extract.yaml")
    if os.path.exists(extract):
        open(extract, "w").close()
        logger.info(f"已清空: {extract}")

    # 清空 Allure 报告
    for d in ["reports/allure-results", "reports/allure-report"]:
        path = os.path.join(base, d)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

    # 日志目录
    os.makedirs(os.path.join(base, "reports", "logs"), exist_ok=True)


# ==================== Fixtures ====================

@pytest.fixture(scope="session")
def config():
    """加载配置文件"""
    return read_yaml(CONFIG_FILE)


@pytest.fixture(scope="session")
def base_url(config):
    """获取当前环境的 base_url"""
    env = config.get("env", "test")
    url = config.get("env_config", {}).get(env, {}).get("base_url", "http://localhost:8080")
    logger.info(f"当前环境: {env} -> {url}")
    return url


@pytest.fixture(scope="session")
def request_util(base_url) -> RequestUtil:
    """创建全局 RequestUtil 实例"""
    req = RequestUtil(base_url=base_url)
    yield req
    req.close()


@pytest.fixture(scope="session")
def user_api(request_util):
    """创建 UserApi 实例"""
    from api.user_api import UserApi
    return UserApi(request_util)


@pytest.fixture(scope="session")
def login_data(config):
    """加载测试数据"""
    data_file = os.path.join(ROOT_DIR, "data", "user_data.yaml")
    return read_yaml(data_file)


# ==================== 日志分隔 ====================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_setup(item):
    logger.info(f"\n{'='*60}")
    logger.info(f"[TEST START] {item.name} - {datetime.now().strftime('%H:%M:%S')}")
    logger.info(f"{'='*60}")
    yield


@pytest.hookimpl(trylast=True, hookwrapper=True)
def pytest_runtest_teardown(item):
    yield
    logger.info(f"{'='*60}")
    logger.info(f"[TEST END] {item.name}")
    logger.info(f"{'='*60}\n")
