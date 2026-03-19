# Jenkinsfile
pipeline {
    agent any

    environment {
        PROJECT_NAME = "auto-api-test"
        BASE_URL = "${env.BASE_URL ?: 'http://auto-test-app:8080'}"
        FEISHU_WEBHOOK_URL = "${env.FEISHU_WEBHOOK_URL ?: ''}"
        PYTHONPATH = "${WORKSPACE}"
    }

    stages {
        stage('📦 Checkout') {
            steps {
                echo "=== 拉取代码 ==="
                git branch: 'main',
                    url: 'https://github.com/kjknb/auto-api-test.git',
                    credentialsId: 'github-ssh-key'
            }
        }

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

        stage('🧪 Test') {
            steps {
                echo "=== 执行测试 ==="
                sh '''
                    export PYTHONPATH=${WORKSPACE}
                    pytest --cache-clear -s -v \
                        --base-url=${BASE_URL} \
                        --alluredir=reports/allure-results || true
                '''
            }
        }

        stage('📊 Report') {
            steps {
                echo "=== 生成报告 ==="
                sh 'allure generate reports/allure-results -o reports/allure-report --clean || true'
                allure([
                    includeProperties: false,
                    results: [[path: 'reports/allure-results']],
                    reportBuildPolicy: 'ALWAYS',
                ])
            }
        }
    }

    post {
        always {
            sh 'rm -rf __pycache__ .pytest_cache'
        }
        success {
            sh '''
                python3 common/notify_feishu.py \
                    "✅ ${PROJECT_NAME} 测试通过 🎉\\n报告: ${BUILD_URL}Allure_Report/" || true
            '''
        }
        failure {
            sh '''
                python3 common/notify_feishu.py \
                    "❌ ${PROJECT_NAME} 测试失败！\\n报告: ${BUILD_URL}Allure_Report/" || true
            '''
        }
    }
}
