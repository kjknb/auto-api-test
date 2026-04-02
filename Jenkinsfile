# ============================================================
# Jenkinsfile
# CI/CD 流水线 —— push 到 main 分支自动触发：安装依赖 → 跑测试 → 生成报告 → 飞书通知
# ============================================================

pipeline {
    agent any

    environment {
        PROJECT_NAME = "auto-api-test"
        // 被测服务地址（默认用 docker-compose 中的服务名）
        BASE_URL = "${env.BASE_URL ?: 'http://auto-test-app:8080'}"
        // 飞书 Webhook（在 Jenkins 环境变量中配置）
        FEISHU_WEBHOOK_URL = "${env.FEISHU_WEBHOOK_URL ?: ''}"
        // Python 模块搜索路径（确保 import 能找到项目模块）
        PYTHONPATH = "${WORKSPACE}"
    }

    stages {
        // ---- 第 1 步：拉取代码 ----
        stage('📦 Checkout') {
            steps {
                echo "=== 拉取代码 ==="
                git branch: 'main',
                    url: 'https://github.com/kjknb/auto-api-test.git',
                    credentialsId: 'github-ssh-key'
            }
        }

        // ---- 第 2 步：安装 Python 依赖 ----
        stage('🐍 Install') {
            steps {
                echo "=== 安装依赖 ==="
                sh '''
                    set -eux
                    command -v pip3 || apt-get install -y python3-pip
                    pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
                    pip3 install -r requirements.txt --break-system-packages
                '''
            }
        }

        // ---- 第 3 步：执行测试（失败会中断流水线） ----
        stage('🧪 Test') {
            steps {
                echo "=== 执行测试 ==="
                sh '''
                    export PYTHONPATH=${WORKSPACE}
                    pytest --cache-clear -s -v \
                        --base-url=${BASE_URL} \
                        --alluredir=reports/allure-results
                '''
            }
        }

        // ---- 第 4 步：生成 Allure 报告 ----
        stage('📊 Report') {
            steps {
                echo "=== 生成报告 ==="
                // allure generate 允许失败（不影响流水线结果）
                sh 'allure generate reports/allure-results -o reports/allure-report --clean || true'
                allure([
                    includeProperties: false,
                    results: [[path: 'reports/allure-results']],
                    reportBuildPolicy: 'ALWAYS',
                ])
            }
        }
    }

    // ---- 流水线结束后的处理 ----
    post {
        // 始终执行：清理缓存文件
        always {
            sh 'rm -rf __pycache__ .pytest_cache'
        }
        // 成功时：飞书通知测试通过
        success {
            sh '''
                python3 common/notify_feishu.py \
                    "✅ ${PROJECT_NAME} 测试通过 🎉\\n报告: ${BUILD_URL}Allure_Report/" || true
            '''
        }
        // 失败时：飞书通知测试失败（仅当测试本身失败时触发）
        failure {
            sh '''
                python3 common/notify_feishu.py \
                    "❌ ${PROJECT_NAME} 测试失败！\\n报告: ${BUILD_URL}Allure_Report/" || true
            '''
        }
    }
}
