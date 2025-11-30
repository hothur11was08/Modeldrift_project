pipeline {
    agent any

    environment {
        DB_URL = credentials('db-credentials-id')   // Jenkins credential ID for DB
        DOCKERHUB = credentials('dockerhub-creds-id') // Jenkins credential ID for DockerHub
    }

    stages {
        stage('Checkout') {
            steps {
                echo "📥 Pulling latest code..."
                checkout scm
            }
        }

        stage('Build API Image') {
            steps {
                echo "🔨 Building Docker image for API..."
                sh 'docker compose build api'
            }
        }

        stage('Deploy Stack') {
            steps {
                echo "🚀 Deploying stack..."
                sh 'docker compose up -d'
            }
        }

        stage('Smoke Test Prediction') {
            steps {
                echo "🧪 Running smoke test..."
                sh 'curl -s http://localhost:8000/predict -o /dev/null -w "%{http_code}"'
            }
        }

        stage('Drift Monitoring') {
            steps {
                echo "📊 Running drift monitoring..."
                sh 'python src/routes/monitor.py'
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up containers..."
            sh 'docker compose down || true'
        }
    }
}

