#!/bin/bash
# scripts/run.sh - 运行测试脚本
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Auto API Test ===${NC}"

# 检查依赖
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}安装依赖...${NC}"
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

# 清理旧报告
rm -rf reports/allure-results reports/allure-report

# 运行测试
echo -e "${GREEN}运行测试...${NC}"
pytest -s -v --alluredir=reports/allure-results "$@"

# 生成报告
if command -v allure &>/dev/null; then
    echo -e "${GREEN}生成报告...${NC}"
    allure generate reports/allure-results -o reports/allure-report --clean
    echo -e "${GREEN}报告: reports/allure-report/index.html${NC}"
else
    echo -e "${YELLOW}未安装 allure CLI，跳过报告生成${NC}"
    echo -e "${YELLOW}安装: https://docs.qameta.io/allure/#_installing_a_commandline${NC}"
fi

echo -e "${GREEN}✅ 完成${NC}"
